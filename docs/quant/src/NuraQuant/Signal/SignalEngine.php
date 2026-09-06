<?php

namespace NuraQuant\Signal;

use NuraQuant\Feature\Indicators;

/**
 * Signal Engine — regime → direction → return-probability → risk-size.
 * Deterministic + point-in-time (uses the exact indicator view at each bar, no lookahead).
 */
final class SignalEngine
{
    /** @param array<int,float> $close @param array<int,float> $high @param array<int,float> $low */
    public function evaluate(array $close, array $high, array $low, float $capital, float $riskPerTrade = 0.02): array
    {
        $n = count($close);
        $i = $n - 1; // current bar
        if ($i < 30) {
            return ['signal' => 'HOLD', 'confidence' => 0.0, 'position' => 0.0, 'rationale' => 'warmup'];
        }

        // ---- REGIME ----
        $hurst = Indicators::hurst($close, 100);
        $adx = Indicators::adx($high, $low, $close, 14)[$i];
        $regime = $this->classifyRegime($hurst, $adx);

        // ---- DIRECTION (trend members) ----
        $emaFast = Indicators::ema($close, 10)[$i];
        $emaSlow = Indicators::ema($close, 40)[$i];
        $donchian = Indicators::donchian($close, $high, $low, 20, 10)[$i];
        $trendScore = 0;
        if ($emaFast !== null && $emaSlow !== null) {
            $trendScore += $emaFast > $emaSlow ? 1 : -1;
        }
        $trendScore += $donchian;

        // ---- RETURN-PROBABILITY (rule-based bayes proxy, XGBoost in P2) ----
        $kama = Indicators::kama($close, 10, 2, 30)[$i];
        $probUp = $this->probUp($trendScore, $kama, $close[$i]??0, $close[$i-1]??0);

        // ---- RISK-SIZE (ATR vol-target) ----
        $atr = Indicators::atr($high, $low, $close, 14)[$i];
        $confidence = abs($probUp - 0.5) * 2; // 0..1
        $direction = $probUp >= 0.5 ? 1 : -1;
        $position = 0.0;
        if ($confidence >= 0.6 && $atr !== null) {
            $position = $direction * Indicators::atrPositionSize($capital, $riskPerTrade, $atr, 2.0);
        }

        return [
            'signal'     => $position > 0 ? 'LONG' : ($position < 0 ? 'SHORT' : 'HOLD'),
            'confidence' => round($confidence, 4),
            'position'   => round($position, 4),
            'regime'     => $regime,
            'prob_up'    => round($probUp, 4),
            'hurst'      => $hurst !== null ? round($hurst, 3) : null,
            'adx'        => $adx !== null ? round($adx, 2) : null,
            'atr'        => $atr !== null ? round($atr, 4) : null,
            'rationale'  => "regime={$regime}; emaF>emaS=" . (($emaFast > $emaSlow) ? 1 : 0) . "; donchian={$donchian}; probUp=" . round($probUp, 3) . "; conf=" . round($confidence, 3),
        ];
    }

    /** H<0.45 range, H>0.55 trend; ADX>25 trending. */
    private function classifyRegime(?float $hurst, ?float $adx): string
    {
        if ($hurst === null) {
            return 'unknown';
        }
        if ($hurst > 0.55 || ($adx !== null && $adx > 25)) {
            return 'trend';
        }
        if ($hurst < 0.45) {
            return 'range';
        }
        return 'transition';
    }

    /** Rule-based probability proxy; replaced by calibrated XGBoost + Bayesian in P2. */
    private function probUp(float $trendScore, ?float $kama, float $cur, float $prev): float
    {
        $score = $trendScore; // -2..2
        $p = 0.5 + $score * 0.13;
        if ($kama !== null && $prev > 0) {
            $p += (($kama - $prev) / $prev) * 0.5; // momentum tilt
        }
        return max(0.05, min(0.95, $p));
    }
}
