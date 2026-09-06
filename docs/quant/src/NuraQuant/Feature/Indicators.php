<?php

namespace NuraQuant\Feature;

/**
 * Deterministic, point-in-time technical indicators.
 * Every function takes only PRIOR data (no future/lookahead) — the walk-forward contract.
 * All pure; unit-testable; seeded/reproducible.
 */
final class Indicators
{
    /**
     * Simple Moving Average. Returns array aligned to input (nulls during warmup).
     * @param array<int,float> $series
     * @return array<int,float|null>
     */
    public static function sma(array $series, int $period): array
    {
        $out = array_fill(0, count($series), null);
        $sum = 0.0;
        for ($i = 0; $i < count($series); $i++) {
            $sum += $series[$i];
            if ($i >= $period) {
                $sum -= $series[$i - $period];
            }
            if ($i >= $period - 1) {
                $out[$i] = $sum / $period;
            }
        }
        return $out;
    }

    /**
     * Exponential Moving Average (Wilder-ish; standard EMA).
     * @return array<int,float|null>
     */
    public static function ema(array $series, int $period): array
    {
        $out = array_fill(0, count($series), null);
        if (count($series) < $period) {
            return $out;
        }
        $k = 2.0 / ($period + 1);
        $seed = array_sum(array_slice($series, 0, $period)) / $period;
        $out[$period - 1] = $seed;
        for ($i = $period; $i < count($series); $i++) {
            $out[$i] = ($series[$i] - $out[$i - 1]) * $k + $out[$i - 1];
        }
        return $out;
    }

    /**
     * Kaufman Adaptive Moving Average (efficiency-ratio weighted). Alpha adapts to noise.
     * @return array<int,float|null>
     */
    public static function kama(array $series, int $period = 10, int $fast = 2, int $slow = 30): array
    {
        $out = array_fill(0, count($series), null);
        if (count($series) < $period + 1) {
            return $out;
        }
        $fastS = 2.0 / ($fast + 1);
        $slowS = 2.0 / ($slow + 1);
        $out[$period] = $series[$period];
        for ($i = $period + 1; $i < count($series); $i++) {
            $change = abs($series[$i] - $series[$i - $period]);
            $vol = 0.0;
            for ($j = $i - $period + 1; $j <= $i; $j++) {
                $vol += abs($series[$j] - $series[$j - 1]);
            }
            $er = $vol === 0.0 ? 0.0 : $change / $vol;
            $sc = ($er * ($fastS - $slowS) + $slowS) ** 2;
            $out[$i] = $out[$i - 1] + $sc * ($series[$i] - $out[$i - 1]);
        }
        return $out;
    }

    /**
     * Average True Range (Wilder smoothing).
     * @param array<int,float> $high @param array<int,float> $low @param array<int,float> $close
     * @return array<int,float|null>
     */
    public static function atr(array $high, array $low, array $close, int $period = 14): array
    {
        $n = count($close);
        $tr = array_fill(0, $n, 0.0);
        for ($i = 1; $i < $n; $i++) {
            $tr[$i] = max(
                $high[$i] - $low[$i],
                abs($high[$i] - $close[$i - 1]),
                abs($low[$i] - $close[$i - 1])
            );
        }
        $out = array_fill(0, $n, null);
        if ($n < $period) {
            return $out;
        }
        $out[$period - 1] = array_sum(array_slice($tr, 0, $period)) / $period;
        for ($i = $period; $i < $n; $i++) {
            $out[$i] = ($out[$i - 1] * ($period - 1) + $tr[$i]) / $period;
        }
        return $out;
    }

    /**
     * Donchian channel breakout (Turtle-style). Long on close > prior N high; flat on close < prior M low.
     * @return array<int,int> position {-1,0,1}
     */
    public static function donchian(array $close, array $high, array $low, int $entry = 20, int $exit = 10): array
    {
        $n = count($close);
        $pos = array_fill(0, $n, 0);
        for ($i = max($entry, $exit); $i < $n; $i++) {
            $priorHigh = max(array_slice($high, $i - $entry, $entry));
            $priorLow = min(array_slice($low, $i - $exit, $exit));
            if ($pos[$i - 1] <= 0 && $close[$i] > $priorHigh) {
                $pos[$i] = 1;
            } elseif ($pos[$i - 1] >= 0 && $close[$i] < $priorLow) {
                $pos[$i] = -1;
            } else {
                $pos[$i] = $pos[$i - 1];
            }
        }
        return $pos;
    }

    /**
     * Average Directional Index (ADX) — trend strength. >25 trending, <20 ranging.
     * @return array<int,float|null>
     */
    public static function adx(array $high, array $low, array $close, int $period = 14): array
    {
        $n = count($close);
        $out = array_fill(0, $n, null);
        if ($n < 2 * $period) {
            return $out;
        }
        $tr = array_fill(0, $n, 0.0);
        $dmPlus = array_fill(0, $n, 0.0);
        $dmMinus = array_fill(0, $n, 0.0);
        for ($i = 1; $i < $n; $i++) {
            $up = $high[$i] - $high[$i - 1];
            $dn = $low[$i - 1] - $low[$i];
            $dmPlus[$i] = ($up > $dn && $up > 0) ? $up : 0.0;
            $dmMinus[$i] = ($dn > $up && $dn > 0) ? $dn : 0.0;
            $tr[$i] = max($high[$i] - $low[$i], abs($high[$i] - $close[$i - 1]), abs($low[$i] - $close[$i - 1]));
        }
        // Wilder smoothing
        $atr = array_fill(0, $n, 0.0);
        $sup = array_fill(0, $n, 0.0);
        $sdn = array_fill(0, $n, 0.0);
        $atr[$period] = array_sum(array_slice($tr, 1, $period));
        $sup[$period] = array_sum(array_slice($dmPlus, 1, $period));
        $sdn[$period] = array_sum(array_slice($dmMinus, 1, $period));
        for ($i = $period + 1; $i < $n; $i++) {
            $atr[$i] = $atr[$i - 1] - $atr[$i - 1] / $period + $tr[$i];
            $sup[$i] = $sup[$i - 1] - $sup[$i - 1] / $period + $dmPlus[$i];
            $sdn[$i] = $sdn[$i - 1] - $sdn[$i - 1] / $period + $dmMinus[$i];
        }
        $dx = array_fill(0, $n, 0.0);
        for ($i = $period; $i < $n; $i++) {
            $dx[$i] = $atr[$i] == 0 ? 0.0 : 100 * abs($sup[$i] - $sdn[$i]) / $atr[$i];
        }
        $adxSum = 0.0;
        $count = 0;
        for ($i = $period * 2 - 1; $i < $n; $i++) {
            $adxSum += $dx[$i];
            $count++;
            if ($count == $period) {
                $out[$i] = $adxSum / $period;
                $adxSum = 0.0;
                $count = 0;
            }
        }
        return $out;
    }

    /**
     * Hurst exponent (rescaled range, point-in-time window). H<0.45 range, H>0.55 trend.
     * @return float|null 0..1
     */
    public static function hurst(array $series, int $window = 100): ?float
    {
        $n = count($series);
        if ($n < $window) {
            return null;
        }
        // work from the last $window closes only (point-in-time)
        $prices = array_slice($series, -$window);
        $m = count($prices);
        $rs = [];
        foreach ([10, 20, 40, 80, 160] as $chunk) {
            if ($chunk >= $m) {
                continue;
            }
            $rsTotal = 0.0;
            $count = 0;
            for ($start = 0; $start + $chunk <= $m; $start += $chunk) {
                $seg = array_slice($prices, $start, $chunk);
                $mean = array_sum($seg) / $chunk;
                $cum = 0.0;
                $maxC = $minC = 0.0;
                $devs = [];
                foreach ($seg as $v) {
                    $cum += $v - $mean;
                    $devs[] = $cum;
                    $maxC = max($maxC, $cum);
                    $minC = min($minC, $cum);
                }
                $std = self::stddev($seg);
                $range = $maxC - $minC;
                if ($std > 0) {
                    $rsTotal += $range / $std;
                    $count++;
                }
            }
            if ($count > 0) {
                $rs[log($chunk)] = log($rsTotal / $count);
            }
        }
        if (count($rs) < 2) {
            return null;
        }
        // simple linear regression slope = H
        $xs = array_keys($rs);
        $ys = array_values($rs);
        $xm = array_sum($xs) / count($xs);
        $ym = array_sum($ys) / count($ys);
        $num = 0.0;
        $den = 0.0;
        foreach ($xs as $i => $x) {
            $num += ($x - $xm) * ($ys[$i] - $ym);
            $den += ($x - $xm) ** 2;
        }
        return $den == 0 ? null : $num / $den;
    }

    /**
     * Volatility-targeted position size. contracts = (capital*risk) / (ATR * stop_multiple).
     */
    public static function atrPositionSize(float $capital, float $riskPerTrade, float $atrValue, float $stopMultiple = 2.0): float
    {
        if ($atrValue <= 0 || $stopMultiple <= 0) {
            return 0.0;
        }
        return $capital * $riskPerTrade / ($atrValue * $stopMultiple);
    }

    /** Standard deviation helper. */
    private static function stddev(array $vals): float
    {
        $n = count($vals);
        if ($n < 2) {
            return 0.0;
        }
        $mean = array_sum($vals) / $n;
        $s = 0.0;
        foreach ($vals as $v) {
            $s += ($v - $mean) ** 2;
        }
        return sqrt($s / ($n - 1));
    }
}
