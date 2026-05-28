#!/usr/bin/env bash
# Quick start script for autonomous vulnerability scanner

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Autonomous Vulnerability Scanner - Quick Start ===${NC}\n"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is required but not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Install dependencies
echo -e "\n${BLUE}Installing dependencies...${NC}"
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create necessary directories
echo -e "\n${BLUE}Setting up directories...${NC}"
mkdir -p logs revenue_data submission_queue learning_models
echo -e "${GREEN}✓ Directories created${NC}"

# Show status
echo -e "\n${BLUE}Current System Status:${NC}"
python3 run_daemon.py status || true

# Show revenue opportunities
echo -e "\n${BLUE}Revenue Opportunities (last 30 days):${NC}"
python3 run_daemon.py roi-report || true

echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "\n${YELLOW}To start the autonomous daemon:${NC}"
echo -e "  ${BLUE}python3 run_daemon.py start${NC}                  # Start in background"
echo -e "  ${BLUE}python3 run_daemon.py start --foreground${NC}    # Start in foreground (debug)"
echo -e "\n${YELLOW}To manage the daemon:${NC}"
echo -e "  ${BLUE}python3 run_daemon.py status${NC}                # Check daemon status"
echo -e "  ${BLUE}python3 run_daemon.py queue${NC}                 # Show submission queue"
echo -e "  ${BLUE}python3 run_daemon.py roi-report${NC}            # Show ROI analysis"
echo -e "  ${BLUE}python3 run_daemon.py export-queue${NC}          # Export queued findings"
echo -e "  ${BLUE}python3 run_daemon.py stop${NC}                  # Stop the daemon"
echo -e "  ${BLUE}python3 run_daemon.py restart${NC}               # Restart the daemon"
echo -e "\n${YELLOW}Revenue tracking:${NC}"
echo -e "  - Payouts recorded in: ${BLUE}revenue_data/payout_history.jsonl${NC}"
echo -e "  - ROI reports in: ${BLUE}revenue_data/program_roi.json${NC}"
echo -e "  - Vulnerability ROI in: ${BLUE}revenue_data/vulnerability_roi.json${NC}"
echo -e "\n${YELLOW}Logs:${NC}"
echo -e "  - Daemon logs: ${BLUE}logs/daemon.log${NC}"
echo -e "  - Event logs: ${BLUE}system-fixer/events.log${NC}"
echo -e "\n"
