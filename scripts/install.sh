#!/bin/bash
#
# MCP-for-Stata Installation Script for macOS and Linux
# https://github.com/sepinetam/mcp-for-stata
#
# Usage:
#   ./install.sh                    # Install to all supported clients
#   ./install.sh -c claude          # Install to Claude Desktop only
#   ./install.sh -c claude -c cc    # Install to Claude Desktop and Claude Code

set -eo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Supported clients
CLIENTS=("claude" "cc" "gemini" "cursor" "cline" "codex" "opencode" "openclaw")

# Open the controlling terminal when available. This keeps prompts working when
# the script itself is being read from a pipe, such as `curl ... | bash`.
open_terminal_input() {
    { exec 3< /dev/tty; } 2> /dev/null
}

# Parse command line arguments
declare -a TARGET_CLIENTS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--client)
            TARGET_CLIENTS+=("$2")
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -c, --client <name>  Target client (can be used multiple times)"
            echo "                       Supported: ${CLIENTS[*]}"
            echo "  -h, --help           Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Install to all clients"
            echo "  $0 -c claude          # Install to Claude Desktop only"
            echo "  $0 -c claude -c cc    # Install to Claude Desktop and Claude Code"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo ""
echo "======================================"
echo "    Install MCP-for-Stata ..."
echo "======================================"
echo ""

# Add common uv installation paths to PATH
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"

# Add uv to PATH when the installer used a supported custom or standard location.
add_uv_to_path() {
    local uv_candidates=()
    local uv_candidate
    local uv_directory

    [[ -n "$UV_INSTALL_DIR" ]] && uv_candidates+=("$UV_INSTALL_DIR/uv")
    [[ -n "$XDG_BIN_HOME" ]] && uv_candidates+=("$XDG_BIN_HOME/uv")
    [[ -n "$XDG_DATA_HOME" ]] && uv_candidates+=("$XDG_DATA_HOME/../bin/uv")
    [[ -n "$CARGO_HOME" ]] && uv_candidates+=("$CARGO_HOME/bin/uv")
    uv_candidates+=("$HOME/.local/bin/uv" "$HOME/.cargo/bin/uv")

    for uv_candidate in "${uv_candidates[@]}"; do
        if [[ -x "$uv_candidate" ]]; then
            uv_directory="$(dirname "$uv_candidate")"
            case ":$PATH:" in
                *":$uv_directory:"*) ;;
                *) export PATH="$uv_directory:$PATH" ;;
            esac
            return 0
        fi
    done

    return 1
}

uv_available() {
    command -v uv &> /dev/null || add_uv_to_path
}

# Check if uv is installed.
check_uv() {
    if uv_available; then
        echo -e "${GREEN}[✓] uv is installed${NC}"
        return 0
    fi

    return 1
}

# Install uv
install_uv() {
    echo -e "${YELLOW}[!] uv is not installed${NC}"
    echo ""
    choice=""
    if open_terminal_input; then
        read -r -p "Do you want to install uv? [Y/n]: " choice <&3 || choice=""
        exec 3<&-
    fi
    case "$choice" in
        n|N|no|No|NO)
            echo -e "${RED}[✗] Installation cancelled.${NC}"
            return 1
            ;;
        *)
            echo ""
            MAX_RETRIES=3
            RETRY_COUNT=0
            while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
                echo "Installing uv... (attempt $((RETRY_COUNT + 1))/$MAX_RETRIES)"
                if curl -LsSf --connect-timeout 30 https://astral.sh/uv/install.sh | sh; then
                    if uv_available; then
                        echo -e "${GREEN}[✓] uv installed successfully${NC}"
                        return 0
                    fi
                    echo -e "${YELLOW}[!] uv was downloaded but could not be found in a standard install location.${NC}"
                fi

                RETRY_COUNT=$((RETRY_COUNT + 1))
                if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
                    echo -e "${YELLOW}[!] Installation failed, retrying in 3 seconds...${NC}"
                    sleep 3
                fi
            done

            echo -e "${RED}[✗] Failed to install uv after $MAX_RETRIES attempts.${NC}"
            echo "    The terminal will remain open when this script was launched by double-clicking."
            echo "    Manual install command: curl -LsSf https://astral.sh/uv/install.sh | sh"
            return 1
            ;;
    esac
}

# Main installation logic
main() {
    # Step 1: Check and install uv
    if ! check_uv; then
        if ! install_uv; then
            echo -e "${RED}[✗] MCP-for-Stata installation stopped because uv is unavailable.${NC}"
            return 1
        fi
    fi

    # Step 2: Install to clients
    if [ ${#TARGET_CLIENTS[@]} -eq 0 ]; then
        # No specific clients specified, install to all
        echo ""
        echo "Installing to all supported clients..."
        if ! uvx stata-mcp install --all; then
            echo -e "${RED}[✗] MCP-for-Stata installation failed. Review the error above.${NC}"
            return 1
        fi
    else
        # Install to specified clients
        for client in "${TARGET_CLIENTS[@]}"; do
            if [[ " ${CLIENTS[*]} " =~ " ${client} " ]]; then
                echo ""
                echo "Installing to $client..."
                if ! uvx stata-mcp install -c "$client"; then
                    echo -e "${RED}[✗] Installation failed for $client. Review the error above.${NC}"
                    return 1
                fi
            else
                echo -e "${RED}[✗] Unknown client: $client${NC}"
                echo "    Supported clients: ${CLIENTS[*]}"
            fi
        done
    fi

    # Step 3: Remind user to restart
    echo ""
    echo "======================================"
    echo -e "${GREEN}[✓] Installation complete!${NC}"
    echo "======================================"
    echo ""
    echo "Please restart your AI client(s) for the changes to take effect."
    echo ""
    echo "For more information, visit: https://www.statamcp.com or https://github.com/sepinetam/mcp-for-stata"
    echo ""
}

if ! main; then
    if [[ "$0" == *.command ]] && open_terminal_input; then
        echo ""
        read -r -p "Press Enter to close this window..." _ <&3 || true
        exec 3<&-
    fi
    exit 1
fi
