<?php

namespace Tests\Unit;

use PHPUnit\Framework\TestCase;
use NuraQuant\Feature\Indicators;
use NuraQuant\Signal\SignalEngine;
use NuraQuant\Risk\RiskManager;

final class QuantTest extends TestCase
{
    private array $close;
    private array $high;
    private array $low;

    protected function setUp(): void
    {
        // deterministic monotonic + noise-free OHLCV for reproducible assertions
        $n = 200;
        $this->close = []; $this->high = []; $this->low = [];
        for ($i = 0; $i < $n; $i++) {
            $c = 100 + $i * 0.5;      // clean uptrend
            $this->close[] = $c;
            $this->high[] = $c + 1.0;
            $this->low[] = $c - 1.0;
        }
    }

    public function test_ema_is_point_in_time(): void
    {
        $ema = Indicators::ema($this->close, 10);
        // warmup nulls, then values; last value depends ONLY on data at that bar
        $this->assertNull($ema[8]);
        $this->assertNotNull($ema[9]);
        $this->assertIsFloat($ema[199]);
        // no lookahead: ema at t must not exceed the max of closes up to t
        $this->assertLessThanOrEqual($this->close[199], $ema[199]);
    }

    public function test_atr_position_size_scales_inversely(): void
    {
        $sizeHigh = Indicators::atrPositionSize(100000, 0.02, 100, 2.0);
        $sizeLow = Indicators::atrPositionSize(100000, 0.02, 200, 2.0);
        // bigger ATR -> smaller size (vol-targeting)
        $this->assertGreaterThan($sizeLow, $sizeHigh);
        $this->assertEquals(10.0, round($sizeHigh, 2)); // 100000*0.02/(100*2)=10
    }

    public function test_signal_engine_uptrend_long(): void
    {
        $engine = new SignalEngine();
        $out = $engine->evaluate($this->close, $this->high, $this->low, 100000, 0.02);
        $this->assertContains($out['signal'], ['LONG', 'HOLD'], 'uptrend should not short');
        $this->assertNotNull($out['atr']);
        $this->assertIsFloat($out['confidence']);
    }

    public function test_risk_ladder_blocks_on_daily_loss(): void
    {
        $rm = new RiskManager(0.05, 0.10, 0.20, 2);
        // down 6% today -> daily-loss-limit veto
        $res = $rm->gate(25.0, 94000, 100000, 100000, 0);
        $this->assertFalse($res['approved']);
        $this->assertStringContainsString('daily-loss-limit', $res['reason']);
        $this->assertEquals(0.0, $res['position']);
    }

    public function test_risk_ladder_circuit_break(): void
    {
        $rm = new RiskManager(0.05, 0.10, 0.20, 2);
        $res = $rm->gate(25.0, 100000, 100000, 100000, 2);
        $this->assertFalse($res['approved']);
        $this->assertStringContainsString('circuit-break', $res['reason']);
    }

    public function test_hurst_classifies_trend_on_monotonic(): void
    {
        $h = Indicators::hurst($this->close, 100);
        $this->assertGreaterThan(0.55, $h, 'monotonic series should yield H>0.55 (trend)');
    }
}
