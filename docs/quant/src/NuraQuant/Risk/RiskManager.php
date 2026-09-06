<?php

namespace NuraQuant\Risk;

/**
 * Risk Manager — the five-layer ladder + independent veto authority.
 * Can block/flag any signal; never accepts a position that breaches a limit.
 */
final class RiskManager
{
    public function __construct(
        private float $dailyLossLimitPct = 0.05,     // layer 2
        private float $weeklyDrawdownPct = 0.10,     // layer 3
        private float $killSwitchPct = 0.20,         // layer 4
        private int $circuitBreak = 2,               // layer 5: consecutive losses -> stop
    ) {}

    /**
     * Evaluate a proposed position against the ladder.
     * @param float $proposedPosition signed units
     * @param float $equity current equity
     * @param float $dayStartEquity start-of-day equity
     * @param float $weeklyPeakEquity week peak
     * @param int $consecutiveLosses running circuit-break counter
     */
    public function gate(
        float $proposedPosition,
        float $equity,
        float $dayStartEquity,
        float $weeklyPeakEquity,
        int $consecutiveLosses,
    ): array {
        $dailyLoss = $this->pct($dayStartEquity, $equity);
        $weeklyDD = $this->pct($weeklyPeakEquity, $equity);

        if ($dailyLoss >= $this->dailyLossLimitPct) {
            return $this->veto('daily-loss-limit', "Daily loss {$dailyLoss}%; limit {$this->dailyLossLimitPct}%");
        }
        if ($weeklyDD >= $this->weeklyDrawdownPct) {
            return $this->veto('weekly-drawdown', "Weekly drawdown {$weeklyDD}%; limit {$this->weeklyDrawdownPct}%");
        }
        if ($this->pct($weeklyPeakEquity, $equity) >= $this->killSwitchPct) {
            return $this->veto('kill-switch', "Drawdown reached {$this->killSwitchPct}% kill-switch");
        }
        if ($consecutiveLosses >= $this->circuitBreak) {
            return $this->veto('circuit-break', "{$consecutiveLosses} consecutive losses; circuit-break reached");
        }
        // Layer 1: per-trade risk is enforced by the position sizing (ATR x riskPerTrade).
        return ['approved' => true, 'position' => $proposedPosition, 'reason' => 'within all limits'];
    }

    private function veto(string $code, string $reason): array
    {
        return ['approved' => false, 'position' => 0.0, 'reason' => "[$code] $reason"];
    }

    private function pct(float $base, float $val): float
    {
        return $base <= 0 ? 0.0 : (($base - $val) / $base);
    }
}
