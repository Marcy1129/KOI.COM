import json
import sys
from web3 import Web3

INFURA_URL = "https://mainnet.infura.io/v3/YOUR_INFURA_ID"

def load_wallet():
    with open("wallet.json", "r") as f:
        return json.load(f)

wallet = load_wallet()
PRIVATE_KEY = wallet["private_key"]
ADDRESS = Web3.to_checksum_address(wallet["address"])

TOKENS = {
    "usdt": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    "usdc": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "dai":  "0x6B175474E89094C44Da98b954EedeAC495271d0F",
    "wbtc": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
    "shib": "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE",
}

ERC20_ABI = [
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "","type":"uint8"}], "type":"function"},
    {"constant": True, "inputs": [{"name":"_owner","type":"address"}], "name": "balanceOf", "outputs": [{"name":"balance","type":"uint256"}], "type":"function"},
    {"constant": False, "inputs": [{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}], "name": "transfer", "outputs": [{"name":"","type":"bool"}], "type":"function"},
]

w3 = Web3(Web3.HTTPProvider(INFURA_URL))

def get_eth_balance():
    balance = w3.eth.get_balance(ADDRESS)
    return w3.from_wei(balance, "ether")

def get_token_balance(symbol):
    contract = w3.eth.contract(address=Web3.to_checksum_address(TOKENS[symbol]), abi=ERC20_ABI)
    decimals = contract.functions.decimals().call()
    balance = contract.functions.balanceOf(ADDRESS).call()
    return balance / (10 ** decimals)

def send_eth(amount, to_addr):
    nonce = w3.eth.get_transaction_count(ADDRESS)
    tx = {
        "nonce": nonce,
        "to": Web3.to_checksum_address(to_addr),
        "value": w3.to_wei(amount, "ether"),
        "gas": 21000,
        "gasPrice": w3.eth.gas_price,
    }
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    print(f"✅ Sent {amount} ETH → {to_addr}")
    print(f"🔗 TX: {w3.to_hex(tx_hash)}")

def send_token(symbol, amount, to_addr):
    contract = w3.eth.contract(address=Web3.to_checksum_address(TOKENS[symbol]), abi=ERC20_ABI)
    decimals = contract.functions.decimals().call()
    nonce = w3.eth.get_transaction_count(ADDRESS)
    tx = contract.functions.transfer(
        Web3.to_checksum_address(to_addr),
        int(amount * (10 ** decimals))
    ).build_transaction({
        "chainId": 1,
        "gas": 100000,
        "gasPrice": w3.eth.gas_price,
        "nonce": nonce,
    })
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    print(f"✅ Sent {amount} {symbol.upper()} → {to_addr}")
    print(f"🔗 TX: {w3.to_hex(tx_hash)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print(" python omni_wallet.py balance")
        print(" python omni_wallet.py eth <amount> <to_address>")
        print(" python omni_wallet.py usdt <amount> <to_address>")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "balance":
        print(f"✅ Connected | Omni Wallet: {ADDRESS}\n")
        print(f"💰 ETH: {get_eth_balance()}")

        for sym in TOKENS.keys():
            bal = get_token_balance(sym)
            print(f"💎 {sym.upper()}: {bal}")

    elif cmd == "eth":
        amt = float(sys.argv[2])
        to = sys.argv[3]
        send_eth(amt, to)

    elif cmd in TOKENS:
        amt = float(sys.argv[2])
        to = sys.argv[3]
        send_token(cmd, amt, to)

    else:
        print("❌ Unknown command")
