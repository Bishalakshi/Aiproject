import streamlit as st
import os
from groq import Groq

API_KEY = os.environ.get("API_KEY")
client = Groq(api_key=API_KEY)

st.set_page_config(page_title="UNO Game", layout="wide")

html_code = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>UNO Game</title>

<style>
body{
    background:#1b1b1b;
    color:white;
    font-family:Arial;
    display:flex;
    flex-direction:column;
    align-items:center;
    padding:20px;
}

h2{margin-bottom:20px;}

.cards{
    display:flex;
    gap:10px;
    flex-wrap:wrap;
    justify-content:center;
    min-height:120px;
}

.card-img{
    width:70px;
    height:100px;
    border-radius:10px;
    object-fit:cover;
    cursor:grab;
    transition:0.2s;
}

.card-img:hover{
    transform:translateY(-5px);
}

.card-back{
    width:70px;
    height:100px;
    border-radius:10px;
    background: radial-gradient(circle at center, #ffeb3b 10%, #e53935 35%, #b71c1c 80%);
    border:3px solid white;
    position:relative;
}

.card-back::before{
    content:"";
    position:absolute;
    width:80%;
    height:50%;
    background:white;
    border-radius:50%;
    top:25%;
    left:10%;
    transform:rotate(-20deg);
}

.card-back::after{
    content:"UNO";
    position:absolute;
    top:35%;
    left:28%;
    color:red;
    font-weight:bold;
    font-size:18px;
    transform:rotate(-20deg);
}

.play-area{
    width:150px;
    height:200px;
    border:3px dashed white;
    border-radius:15px;
    display:flex;
    align-items:center;
    justify-content:center;
    margin:20px;
}

.deck{
    width:70px;
    height:100px;
    background:#333;
    border-radius:10px;
    display:flex;
    align-items:center;
    justify-content:center;
    cursor:pointer;
    margin-bottom:10px;
    color:white;
    font-weight:bold;
}

.scoreboard{
    display:flex;
    gap:40px;
    margin:10px 0;
    font-size:18px;
    font-weight:bold;
}

.score-box{
    background:#333;
    padding:10px 20px;
    border-radius:10px;
    text-align:center;
}

.btn{
    background:#e53935;
    color:white;
    border:none;
    padding:10px 20px;
    border-radius:10px;
    cursor:pointer;
    font-size:16px;
    margin:5px;
}

.btn:hover{
    background:#b71c1c;
}

.hint-box{
    background:#333;
    padding:10px 20px;
    border-radius:10px;
    margin:10px;
    font-size:14px;
    min-width:300px;
    text-align:center;
    display:none;
}

.message-box{
    background:#444;
    padding:8px 20px;
    border-radius:10px;
    margin:5px;
    font-size:14px;
    color:#ffeb3b;
    min-height:30px;
    text-align:center;
}

/* WINNER POPUP */
.popup-overlay{
    display:none;
    position:fixed;
    top:0; left:0;
    width:100%; height:100%;
    background:rgba(0,0,0,0.8);
    z-index:1000;
    align-items:center;
    justify-content:center;
}

.popup-overlay.show{
    display:flex;
}

.popup-box{
    background:#222;
    border:3px solid #ffeb3b;
    border-radius:20px;
    padding:40px;
    text-align:center;
    font-size:24px;
    font-weight:bold;
}

.popup-box h1{
    font-size:48px;
    margin-bottom:10px;
}

.popup-box button{
    margin-top:20px;
    background:#e53935;
    color:white;
    border:none;
    padding:12px 30px;
    border-radius:10px;
    font-size:18px;
    cursor:pointer;
}
</style>
</head>
<body>

<!-- WINNER POPUP -->
<div class="popup-overlay" id="popup-overlay">
    <div class="popup-box">
        <h1 id="popup-emoji">🎉</h1>
        <div id="popup-msg">You Win!</div>
        <button onclick="restartGame()">Play Again</button>
    </div>
</div>

<h2>🃏 UNO Game</h2>

<!-- SCOREBOARD -->
<div class="scoreboard">
    <div class="score-box">
        👤 Your Score<br>
        <span id="user-score">0</span>
    </div>
    <div class="score-box">
        🤖 System Score<br>
        <span id="system-score">0</span>
    </div>
</div>

<div class="message-box" id="message-box">Game started! Your turn.</div>

<h3>🤖 System (<span id="system-count">7</span> cards)</h3>
<div class="cards" id="system-cards"></div>

<br>
<div class="deck" id="draw-deck">🂠 DRAW</div>

<div class="play-area" id="play-area"></div>

<h3>👤 Your Hand</h3>
<div class="cards" id="user-cards"></div>

<br>
<button class="btn" onclick="getHint()">💡 AI Hint</button>
<button class="btn" onclick="restartGame()">🔄 Restart</button>
<div class="hint-box" id="hint-box">Hint will appear here...</div>

<script>
const GITHUB_RAW = "https://raw.githubusercontent.com/Bishalakshi/Aiproject/main/static/";
const colors = ["Red","Yellow","Green","Blue"];
const numbers = ["0","1","2","3","4","5","6","7","8","9"];
const specials = ["Skip","Reverse","Draw_2"];
const wilds = ["Wild","Wild_Draw_4"];

let deck = [];
let userHand = [];
let systemHand = [];
let topCard = null;
let userScore = 0;
let systemScore = 0;

// =====================
// DECK
// =====================
function createDeck(){
    deck = [];
    colors.forEach(color => {
        numbers.forEach(num => {
            deck.push(color + "_" + num);
        });
        specials.forEach(sp => {
            deck.push(color + "_" + sp);
        });
    });
    wilds.forEach(w => {
        deck.push(w);
        deck.push(w);
        deck.push(w);
        deck.push(w);
    });
}

function shuffle(){
    deck.sort(() => Math.random() - 0.5);
}

function deal(){
    userHand = deck.splice(0, 7);
    systemHand = deck.splice(0, 7);
    topCard = deck.pop();
}

// =====================
// SCORE
// =====================
function cardScore(card){
    if(card.includes("Wild")) return 50;
    if(card.includes("Skip") || card.includes("Reverse") || card.includes("Draw_2")) return 20;
    const num = parseInt(card.split("_").pop());
    return isNaN(num) ? 0 : num;
}

function updateScore(){
    userScore = systemHand.reduce((s, c) => s + cardScore(c), 0);
    systemScore = userHand.reduce((s, c) => s + cardScore(c), 0);
    document.getElementById("user-score").innerText = userScore;
    document.getElementById("system-score").innerText = systemScore;
}

// =====================
// RENDER
// =====================
function render(){
    renderUser();
    renderSystem();
    renderTop();
    updateScore();
    document.getElementById("system-count").innerText = systemHand.length;
}

function makeCardImg(card, draggable, index){
    const img = document.createElement("img");
    img.src = GITHUB_RAW + card + ".jpg";
    img.className = "card-img";
    img.draggable = draggable;
    img.title = card;

    img.onerror = function(){
        this.style.display = 'none';
        const div = document.createElement("div");
        div.style.cssText = "width:70px;height:100px;border-radius:10px;background:#555;display:flex;align-items:center;justify-content:center;color:white;font-size:10px;text-align:center;padding:5px;cursor:grab;";
        div.innerText = card;
        if(draggable){
            div.draggable = true;
            div.ondragstart = (e) => { e.dataTransfer.setData("index", index); };
        }
        this.parentNode.appendChild(div);
    };

    if(draggable){
        img.ondragstart = (e) => {
            e.dataTransfer.setData("index", index);
        };
    }

    return img;
}

function renderUser(){
    const container = document.getElementById("user-cards");
    container.innerHTML = "";
    userHand.forEach((card, index) => {
        container.appendChild(makeCardImg(card, true, index));
    });
}

function renderSystem(){
    const container = document.getElementById("system-cards");
    container.innerHTML = "";
    systemHand.forEach(() => {
        const div = document.createElement("div");
        div.className = "card-back";
        container.appendChild(div);
    });
}

function renderTop(){
    const area = document.getElementById("play-area");
    area.innerHTML = "";
    const img = makeCardImg(topCard, false, -1);
    img.style.width = "120px";
    img.style.height = "180px";
    area.appendChild(img);
}

// =====================
// VALID MOVE
// =====================
function isValid(card){
    if(card.includes("Wild")) return true;
    const topParts = topCard.split("_");
    const cardParts = card.split("_");
    return topParts[0] === cardParts[0] || topParts[1] === cardParts[1];
}

// =====================
// DRAG & DROP PLAY
// =====================
document.getElementById("play-area").ondragover = (e) => e.preventDefault();

document.getElementById("play-area").ondrop = (e) => {
    const index = e.dataTransfer.getData("index");
    const selected = userHand[index];

    if(isValid(selected)){
        topCard = selected;
        userHand.splice(index, 1);
        setMessage("You played " + selected);
        render();

        if(userHand.length === 0){
            showWinner("user");
            return;
        }

        setTimeout(aiMove, 1000);
    } else {
        alert("❌ Invalid move! Card must match color or number.");
    }
};

// =====================
// DRAW
// =====================
document.getElementById("draw-deck").onclick = () => {
    if(deck.length > 0){
        userHand.push(deck.pop());
        setMessage("You drew a card.");
        render();
        setTimeout(aiMove, 1000);
    } else {
        setMessage("Deck is empty!");
    }
};

// =====================
// AI MOVE
// =====================
function aiMove(){
    let played = false;

    for(let i = 0; i < systemHand.length; i++){
        if(isValid(systemHand[i])){
            topCard = systemHand[i];
            systemHand.splice(i, 1);
            played = true;
            setMessage("🤖 System played " + topCard);
            break;
        }
    }

    if(!played && deck.length > 0){
        systemHand.push(deck.pop());
        setMessage("🤖 System drew a card.");
    }

    render();

    if(systemHand.length === 0){
        showWinner("system");
    }
}

// =====================
// MESSAGE
// =====================
function setMessage(msg){
    document.getElementById("message-box").innerText = msg;
}

// =====================
// WINNER POPUP
// =====================
function showWinner(winner){
    const overlay = document.getElementById("popup-overlay");
    const msg = document.getElementById("popup-msg");
    const emoji = document.getElementById("popup-emoji");

    if(winner === "user"){
        emoji.innerText = "🎉";
        msg.innerText = "You Win! Congratulations!";
    } else {
        emoji.innerText = "😢";
        msg.innerText = "System Wins! Better luck next time!";
    }

    overlay.classList.add("show");
}

// =====================
// RESTART
// =====================
function restartGame(){
    document.getElementById("popup-overlay").classList.remove("show");
    document.getElementById("hint-box").style.display = "none";
    createDeck();
    shuffle();
    deal();
    setMessage("Game started! Your turn.");
    render();
}

// =====================
// AI HINT (Groq)
// =====================
async function getHint(){
    const hintBox = document.getElementById("hint-box");
    hintBox.style.display = "block";
    hintBox.innerText = "⏳ Getting hint from AI...";

    const playable = userHand.filter(c => isValid(c));

    if(playable.length === 0){
        hintBox.innerText = "💡 No playable cards. Draw a card!";
        return;
    }

    try {
        const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer """ + API_KEY + """"
            },
            body: JSON.stringify({
                model: "llama3-8b-8192",
                messages: [{
                    role: "user",
                    content: "You are an UNO expert. Top card: " + topCard + ". My playable cards: " + playable.join(", ") + ". System has " + systemHand.length + " cards. Which card should I play and why? Keep it under 2 sentences."
                }],
                max_tokens: 100
            })
        });

        const data = await response.json();
        hintBox.innerText = "💡 " + data.choices[0].message.content;
    } catch(e) {
        hintBox.innerText = "💡 Best card to play: " + playable[0];
    }
}

// =====================
// START
// =====================
createDeck();
shuffle();
deal();
render();
</script>

</body>
</html>
"""

st.components.v1.html(html_code, height=900, scrolling=True)











