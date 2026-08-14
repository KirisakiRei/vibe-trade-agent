/**
 * PM2 ecosystem config for the Vibe-Trading Telegram bot (VPS, no Docker).
 *
 * Prerequisites (run once on the VPS):
 *   cd /home/ubuntu/vibe-trade-agent        # ← adjust APP_DIR below
 *   cd agent && python3.11 -m venv .venv && source .venv/bin/activate
 *   pip install --no-deps -e . && pip install -r requirements-channels.txt
 *   deactivate
 *
 * Config files the bot reads at startup:
 *   ~/.vibe-trading/.env        → LLM keys, VIBE_TRADING_ANALYSIS_ONLY,
 *                                  VIBE_TRADING_ENABLE_SCHEDULER, TELEGRAM_*
 *   ~/.vibe-trading/agent.json  → channels.telegram { token, allowFrom,
 *                                  allowlistEnabled, groupPolicy }
 *
 * Usage:
 *   pm2 start ecosystem.config.js
 *   pm2 save && pm2 startup     # auto-restart on reboot
 *   pm2 logs vibe-trading
 */
module.exports = {
  apps: [
    {
      name: "vibe-trading",
      // Console-script entry installed into the venv during setup.
      script: "agent/.venv/bin/vibe-trading",
      args: "serve --host 127.0.0.1 --port 8899",
      cwd: "/home/ubuntu/vibe-trade-agent",
      interpreter: "none", // venv console script is already a Python shim
      instances: 1,        // single long-polling Telegram worker; keep at 1
      exec_mode: "fork",   // fork (not cluster) — Python single-process
      env: {
        NODE_ENV: "production",
        PYTHONUNBUFFERED: "1",
        // Optional: pin the runtime root if the deploy user's HOME is shared.
        // VIBE_TRADING_HOME: "/home/ubuntu/.vibe-trading",
      },
      out_file: "~/.pm2/logs/vibe-trading-out.log",
      error_file: "~/.pm2/logs/vibe-trading-error.log",
      merge_logs: true,
      max_memory_restart: "4G",
      time: true, // timestamps in pm2 logs
      restart_delay: 3000,
      // Exponential backoff after crashes, capped at 30s.
      exp_backoff_restart_delay: 100,
      max_restarts: 20,
      watch: false,
      kill_timeout: 15000,
      listen_timeout: 120000,
    },
  ],
};