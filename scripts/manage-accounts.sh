#!/bin/bash

# Tenxsom AI Multi-Account Management Script
# Manages UseAPI.net account pool for load balancing

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_ROOT/accounts.json"
ENV_FILE="$PROJECT_ROOT/production-config.env"

# Load environment
if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Functions
show_help() {
    cat << EOF
Tenxsom AI Account Management

Usage: $0 [command] [options]

Commands:
    add         Add a new account to the pool
    remove      Remove an account from the pool
    list        List all accounts and their status
    check       Check credits for all accounts
    balance     Show load balancing statistics
    emergency   Switch all accounts to LTX Turbo mode
    test        Test video generation across accounts

Options:
    -h, --help  Show this help message

Examples:
    $0 add tenxsom.ai.1@gmail.com user:XXXX-XXXXXXXXXXXXXXXXXX
    $0 check
    $0 emergency
EOF
}

# Initialize accounts.json if not exists
init_config() {
    if [ ! -f "$CONFIG_FILE" ]; then
        echo "Creating initial accounts configuration..."
        cat > "$CONFIG_FILE" << EOF
{
  "accounts": [
    {
      "id": "primary",
      "email": "goldensonproperties@gmail.com",
      "bearer_token": "$USEAPI_BEARER_TOKEN",
      "models": ["veo2", "ltx-turbo", "flux"],
      "priority": 1,
      "credit_limit": 5000,
      "active": true
    }
  ],
  "strategy": "cost_optimized",
  "health_check_interval": 300
}
EOF
        echo -e "${GREEN}✅ Created accounts.json${NC}"
    fi
}

# Add new account
add_account() {
    local email="$1"
    local token="$2"
    
    if [ -z "$email" ] || [ -z "$token" ]; then
        echo -e "${RED}Error: Email and token required${NC}"
        echo "Usage: $0 add <email> <token>"
        exit 1
    fi
    
    # Validate token format
    if [[ ! "$token" =~ ^user:[0-9]+-[a-zA-Z0-9]+$ ]]; then
        echo -e "${RED}Error: Invalid token format${NC}"
        echo "Expected: user:XXXX-XXXXXXXXXXXXXXXXXX"
        exit 1
    fi
    
    # Generate account ID
    local account_id=$(echo "$email" | sed 's/@.*//g' | sed 's/\./-/g')
    
    # Check if account exists
    if jq -e ".accounts[] | select(.email == \"$email\")" "$CONFIG_FILE" > /dev/null 2>&1; then
        echo -e "${YELLOW}Account $email already exists${NC}"
        exit 1
    fi
    
    # Determine account type based on email
    local models='["ltx-turbo"]'
    local priority=2
    local credit_limit=0
    
    if [[ "$email" == *"premium"* ]]; then
        models='["veo2", "ltx-turbo", "flux"]'
        priority=1
        credit_limit=5000
    fi
    
    # Add account to config
    jq ".accounts += [{
        \"id\": \"$account_id\",
        \"email\": \"$email\",
        \"bearer_token\": \"$token\",
        \"models\": $models,
        \"priority\": $priority,
        \"credit_limit\": $credit_limit,
        \"active\": true
    }]" "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"
    
    echo -e "${GREEN}✅ Added account: $email${NC}"
    echo "Models: $(echo $models | jq -r '. | join(", ")')"
    echo "Priority: $priority"
    
    # Test the account
    echo "Testing account..."
    test_account "$token"
}

# Remove account
remove_account() {
    local email="$1"
    
    if [ -z "$email" ]; then
        echo -e "${RED}Error: Email required${NC}"
        echo "Usage: $0 remove <email>"
        exit 1
    fi
    
    # Check if account exists
    if ! jq -e ".accounts[] | select(.email == \"$email\")" "$CONFIG_FILE" > /dev/null 2>&1; then
        echo -e "${RED}Account $email not found${NC}"
        exit 1
    fi
    
    # Remove account
    jq ".accounts = [.accounts[] | select(.email != \"$email\")]" "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"
    
    echo -e "${GREEN}✅ Removed account: $email${NC}"
}

# List all accounts
list_accounts() {
    echo "📊 Tenxsom AI Account Pool"
    echo "=========================="
    
    local total=$(jq '.accounts | length' "$CONFIG_FILE")
    echo "Total accounts: $total"
    echo ""
    
    # Display each account
    jq -r '.accounts[] | 
        "ID: \(.id)\n" +
        "Email: \(.email)\n" +
        "Models: \(.models | join(", "))\n" +
        "Priority: \(.priority)\n" +
        "Credit Limit: \(.credit_limit)\n" +
        "Active: \(.active)\n" +
        "---"' "$CONFIG_FILE"
}

# Check credits for all accounts
check_credits() {
    echo "💰 Checking account credits..."
    echo "============================="
    
    local total_credits=0
    
    # Read accounts and check each
    while IFS= read -r account; do
        local email=$(echo "$account" | jq -r '.email')
        local token=$(echo "$account" | jq -r '.bearer_token')
        local models=$(echo "$account" | jq -r '.models | join(", ")')
        
        echo -n "Checking $email... "
        
        # Call API to check credits
        local response=$(curl -s -H "Authorization: Bearer $token" \
            "https://api.useapi.net/v1/accounts/credits" 2>/dev/null || echo '{"error": true}')
        
        if echo "$response" | jq -e '.error' > /dev/null 2>&1; then
            echo -e "${RED}Failed${NC}"
        else
            local credits=$(echo "$response" | jq -r '.credits // 0')
            total_credits=$((total_credits + credits))
            
            if [ "$credits" -lt 1000 ]; then
                echo -e "${YELLOW}$credits credits (Low)${NC}"
            else
                echo -e "${GREEN}$credits credits${NC}"
            fi
            
            # Show model availability
            if [[ "$models" == *"ltx-turbo"* ]]; then
                echo "  └─ LTX Turbo available (0 credits/video)"
            fi
        fi
    done < <(jq -c '.accounts[]' "$CONFIG_FILE")
    
    echo ""
    echo "Total credits across all accounts: $total_credits"
}

# Show load balancing statistics
show_balance() {
    echo "⚖️  Load Balancing Statistics"
    echo "============================"
    
    local strategy=$(jq -r '.strategy' "$CONFIG_FILE")
    echo "Strategy: $strategy"
    echo ""
    
    # Count accounts by type
    local premium_count=$(jq '[.accounts[] | select(.models | contains(["veo2"]))] | length' "$CONFIG_FILE")
    local ltx_count=$(jq '[.accounts[] | select(.models | contains(["ltx-turbo"]))] | length' "$CONFIG_FILE")
    local total=$(jq '.accounts | length' "$CONFIG_FILE")
    
    echo "Account Distribution:"
    echo "  Premium accounts (Veo2): $premium_count"
    echo "  Volume accounts (LTX): $ltx_count"
    echo "  Total accounts: $total"
    echo ""
    
    # Calculate capacity
    local youtube_capacity=$((premium_count * 12))  # 12 videos/day per premium account
    local volume_capacity=$((ltx_count * 1000))     # Virtually unlimited with LTX Turbo
    
    echo "Daily Capacity:"
    echo "  YouTube (Premium): ~$youtube_capacity videos/day"
    echo "  TikTok/Instagram: ~$volume_capacity videos/day"
    echo ""
    
    # Cost estimation
    local monthly_cost=$((28 + (ltx_count * 15)))
    echo "Estimated Monthly Cost: \$$monthly_cost"
}

# Emergency mode - switch all to LTX Turbo
emergency_mode() {
    echo -e "${YELLOW}🚨 EMERGENCY MODE: Switching all accounts to LTX Turbo only${NC}"
    
    # Create backup
    cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%s)"
    
    # Update all accounts to LTX Turbo only
    jq '.accounts = [.accounts[] | 
        if .models | contains(["ltx-turbo"]) then
            .models = ["ltx-turbo"] | .credit_limit = 0
        else . end]' "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"
    
    echo -e "${GREEN}✅ All compatible accounts switched to LTX Turbo mode${NC}"
    echo "Backup saved to: $CONFIG_FILE.backup.*"
}

# Test account
test_account() {
    local token="$1"
    
    # Test credit check
    local response=$(curl -s -H "Authorization: Bearer $token" \
        "https://api.useapi.net/v1/accounts/credits" 2>/dev/null)
    
    if echo "$response" | jq -e '.credits' > /dev/null 2>&1; then
        local credits=$(echo "$response" | jq -r '.credits')
        echo -e "${GREEN}✅ Account verified - Credits: $credits${NC}"
        return 0
    else
        echo -e "${RED}❌ Account verification failed${NC}"
        return 1
    fi
}

# Test video generation across accounts
test_generation() {
    echo "🎬 Testing video generation across account pool"
    echo "=============================================="
    
    local test_prompt="A serene landscape with mountains and a lake at sunset"
    
    # Test LTX Turbo on each account
    while IFS= read -r account; do
        local email=$(echo "$account" | jq -r '.email')
        local token=$(echo "$account" | jq -r '.bearer_token')
        local models=$(echo "$account" | jq -r '.models[]')
        
        if [[ "$models" == *"ltx-turbo"* ]]; then
            echo "Testing LTX Turbo on $email..."
            
            # Would implement actual video generation test here
            echo "  └─ [Simulated] Would generate video with LTX Turbo (0 credits)"
        fi
    done < <(jq -c '.accounts[]' "$CONFIG_FILE")
}

# Main script logic
main() {
    init_config
    
    case "$1" in
        add)
            add_account "$2" "$3"
            ;;
        remove)
            remove_account "$2"
            ;;
        list)
            list_accounts
            ;;
        check)
            check_credits
            ;;
        balance)
            show_balance
            ;;
        emergency)
            emergency_mode
            ;;
        test)
            test_generation
            ;;
        -h|--help|"")
            show_help
            ;;
        *)
            echo -e "${RED}Unknown command: $1${NC}"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"