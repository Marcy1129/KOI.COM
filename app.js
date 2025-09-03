// Basic Web3 wallet logic (before ethers fix)

// connect to provider
let web3;
if (window.ethereum) {
  web3 = new Web3(window.ethereum);
  window.ethereum.request({ method: "eth_requestAccounts" });
} else {
  alert("No Ethereum provider found. Please install MetaMask.");
}

let account;

// get accounts
async function loadAccount() {
  const accounts = await web3.eth.getAccounts();
  account = accounts[0];
  document.getElementById("walletAddress").innerText = `Address: ${account}`;
  loadBalance();
}

async function loadBalance() {
  if (!account) return;
  const balance = await web3.eth.getBalance(account);
  const ethBalance = web3.utils.fromWei(balance, "ether");
  document.getElementById("balance").innerText = `Balance: ${ethBalance} ETH`;
}

async function sendTransaction() {
  const toAddress = document.getElementById("toAddress").value;
  const amount = document.getElementById("amount").value;
  const value = web3.utils.toWei(amount, "ether");

  try {
    await web3.eth.sendTransaction({
      from: account,
      to: toAddress,
      value: value
    });
    alert("Transaction sent!");
    loadBalance();
  } catch (error) {
    console.error(error);
    alert("Transaction failed.");
  }
}

// load on startup
window.addEventListener("load", () => {
  loadAccount();
});
