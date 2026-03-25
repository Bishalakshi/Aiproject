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
    padding:5px;
    transform:scale(0.85);
    transform-origin:top center;
    overflow:hidden;
}

h2{ margin-bottom:5px; font-size:20px; }
h3{ margin:3px 0; font-size:15px; }

.cards{
    display:flex;
    gap:6px;
    flex-wrap:wrap;
    justify-content:center;
    min-height:85px;
}

.card-img{
    width:55px;
    height:80px;
    border-radius:8px;
    object-fit:cover;
    cursor:grab;
    transition:0.2s;
}

.card-img:hover{
    transform:translateY(-5px);
}

.card-back{
    width:55px;
    height:80px;
    border-radius:8px;
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
    font-size:14px;
    transform:rotate(-20deg);
}

.play-area{
    width:110px;
    height:150px;
    border:3px dashed white;
    border-radius:15px;
    display:flex;
    align-items:center;
    justify-content:center;
    margin:8px;
    position:relative;
}

.deck{
    width:55px;
    height:80px;
    background:#333;
    border-radius:8px;
    display:flex;
    align-items:center;
    justify-content:center;
    cursor:pointer;
    margin-bottom:5px;
    color:white;
    font-weight:bold;
    font-size:12px;
}

.scoreboard{
    display:flex;
    gap:30px;
    margin:5px 0;
    font-size:15px;
    font-weight:bold;
}

.score-box{
    background:#333;
    padding:6px 15px;
    border-radius:10px;
    text-align:center;
    font-size:15px;
}

.btn{
    background:#e53935;
    color:white;
    border:none;
    padding:7px 14px;
    border-radius:10px;
    cursor:pointer;
    font-size:13px;
    margin:3px;
}

.btn:hover{
    background:#b71c1c;
}

.hint-box{
    background:#333;
    padding:8px 15px;
    border-radius:10px;
    margin:5px;
    font-size:13px;
    min-width:280px;
    text-align:center;
    display:none;
}

.message-box{
    background:#444;
    padding:6px 20px;
    border-radius:10px;
    margin:4px;
    font-size:13px;
    color:#ffeb3b;
    min-height:25px;
    text-align:center;
}

.color-picker{
    display:none;
    gap:10px;
    margin:5px;
    justify-content:center;
}

.color-btn{
    width:40px;
    height:40px;
    border-radius:50%;
    border:3px solid white;
    cursor:pointer;
    font-size:10px;
    font-weight:bold;
}

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
    padding:30px;
    text-align:center;
    font-size:20px;
    font-weight:bold;
}

.popup-box h1{
    font-size:40px;
    margin-bottom:10px;
}

.popup-box button{
    margin-top:15px;
    background:#e53935;
    color:white;
    border:none;
    padding:10px 25px;
    border-radius:10px;
    font-size:16px;
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

<div class="color-picker" id="color-picker">
    <button class="color-btn" style="background:red" onclick="chooseColor('Red')">Red</button>
    <button class="color-btn" style="background:blue" onclick="chooseColor('Blue')">Blue</button>
    <button class="color-btn" style="background:green" onclick="chooseColor('Green')">Green</button>
    <button class="color-btn" style="background:#FFD700;color:black" onclick="chooseColor('Yellow')">Yellow</button>
</div>

<h3>👤 Your Hand</h3>
<div class="cards" id="user-cards"></div>

<br>
<button class="btn" onclick="getHint()">💡 AI Hint</button>
<button class="btn" onclick="callUno()">🗣️ UNO!</button>
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
let currentColor = null;
let userScore = 0;
let systemScore = 0;
let pendingWildCard = null;
let playerTurn = true;

function createDeck(){
    deck = [];
    colors.forEach(color => {
        numbers.forEach(num => {
            deck.push(color + "_" + num + ".jpg");
        });
        specials.forEach(sp => {
            deck.push(color + "_" + sp + ".jpg");
        });
    });
    for(let i=0;i<4;i++){
        deck.push("Wild.jpg");
        deck.push("Wild_Draw_4.jpg");
    }
}

function shuffle(){
    deck.sort(() => Math.random() - 0.5);
}

function drawCard(){
    if(deck.length === 0) return null;
    return deck.pop();
}

function deal(){
    userHand = [];
    systemHand = [];
    for(let i=0;i<7;i++){
        userHand.push(drawCard());
        systemHand.push(drawCard());
    }
    do {
        topCard = drawCard();
    } while(topCard === "Wild_Draw_4.jpg");

    if(topCard.startsWith("Wild")){
        currentColor = colors[Math.floor(Math.random()*colors.length)];
    } else {
        currentColor = topCard.split("_")[0];
    }
    playerTurn = true;
}

function cardScore(card){
    if(card.includes("Wild")) return 50;
    if(card.includes("Skip") || card.includes("Reverse") || card.includes("Draw_2")) return 20;
    const parts = card.replace(".jpg","").split("_");
    const num = parseInt(parts[parts.length-1]);
    return isNaN(num) ? 0 : num;
}

function updateScore(){
    userScore = systemHand.reduce((s,c) => s + cardScore(c), 0);
    systemScore = userHand.reduce((s,c) => s + cardScore(c), 0);
    document.getElementById("user-score").innerText = userScore;
    document.getElementById("system-score").innerText = systemScore;
    document.getElementById("system-count").innerText = systemHand.length;
}

function render(){
    renderUser();
    renderSystem();
    renderTop();
    updateScore();
}

function makeCardImg(card, draggable, index){
    const wrapper = document.createElement("div");
    wrapper.style.position = "relative";

    const img = document.createElement("img");
    img.src = GITHUB_RAW + card;
    img.className = "card-img";
    img.draggable = draggable;
    img.title = card.replace(".jpg","");

    img.onerror = function(){
        this.style.display = "none";
        const div = document.createElement("div");
        div.style.cssText = "width:55px;height:80px;border-radius:8px;background:#555;display:flex;align-items:center;justify-content:center;color:white;font-size:9px;text-align:center;padding:3px;cursor:grab;";
        div.innerText = card.replace(".jpg","");
        if(draggable){
            div.draggable = true;
            div.ondragstart = (e) => { e.dataTransfer.setData("index", index); };
            div.onclick = () => { playCard(index); };
        }
        wrapper.appendChild(div);
    };

    if(draggable){
        img.ondragstart = (e) => { e.dataTransfer.setData("index", index); };
        img.onclick = () => { playCard(index); };
    }

    wrapper.appendChild(img);
    return wrapper;
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
    const img = document.createElement("img");
    img.src = GITHUB_RAW + topCard;
    img.className = "card-img";
    img.style.width = "90px";
    img.style.height = "130px";
    img.style.borderRadius = "10px";

    if(topCard.includes("Wild")){
        const colorDiv = document.createElement("div");
        colorDiv.style.cssText = "position:absolute;bottom:-20px;font-size:11px;color:#ffeb3b;";
        colorDiv.innerText = "Color: " + currentColor;
        area.appendChild(colorDiv);
    }

    area.appendChild(img);
}

function isValid(card){
    if(card.includes("Wild")) return true;
    const cardColor = card.split("_")[0];
    const cardVal = card.replace(".jpg","").split("_").pop();
    const topVal = topCard.replace(".jpg","").split("_").pop();
    return cardColor === currentColor || cardVal === topVal;
}

function playCard(index){
    if(!playerTurn) return;
    const selected = userHand[index];
    if(!isValid(selected)){
        setMessage("❌ Invalid move! Must match color or value.");
        return;
    }
    if(selected.includes("Wild")){
        pendingWildCard = {card: selected, index: index};
        document.getElementById("color-picker").style.display = "flex";
        setMessage("🎨 Choose a color for your Wild card!");
        return;
    }
    applyPlayerCard(selected, index, currentColor);
}

function chooseColor(color){
    document.getElementById("color-picker").style.display = "none";
    if(pendingWildCard){
        applyPlayerCard(pendingWildCard.card, pendingWildCard.index, color);
        pendingWildCard = null;
    }
}

function applyPlayerCard(card, index, chosenColor){
    userHand.splice(index, 1);
    topCard = card;
    currentColor = card.includes("Wild") ? chosenColor : card.split("_")[0];
    setMessage("You played " + card.replace(".jpg",""));

    if(card.includes("Skip") || card.includes("Reverse")){
        render();
        setMessage("System is skipped! Your turn again.");
        return;
    }

    if(card.includes("Draw_2")){
        for(let i=0;i<2;i++) { const c=drawCard(); if(c) systemHand.push(c); }
        setMessage("System draws 2 cards! Your turn again.");
        render();
        return;
    }

    if(card.includes("Wild_Draw_4")){
        for(let i=0;i<4;i++) { const c=drawCard(); if(c) systemHand.push(c); }
        setMessage("System draws 4 cards! Your turn again.");
        render();
        return;
    }

    render();

    if(userHand.length === 0){
        showWinner("user");
        return;
    }

    playerTurn = false;
    setTimeout(aiMove, 1200);
}

document.getElementById("play-area").ondragover = (e) => e.preventDefault();
document.getElementById("play-area").ondrop = (e) => {
    const index = parseInt(e.dataTransfer.getData("index"));
    playCard(index);
};

document.getElementById("draw-deck").onclick = () => {
    if(!playerTurn) return;
    const c = drawCard();
    if(c){
        userHand.push(c);
        setMessage("You drew: " + c.replace(".jpg",""));
        render();
        playerTurn = false;
        setTimeout(aiMove, 1200);
    } else {
        setMessage("Deck is empty!");
    }
};

function aiMove(){
    if(systemHand.length === 0){ showWinner("system"); return; }

    const playable = systemHand.filter(c => isValid(c));

    if(playable.length > 0){
        let card = playable.find(c => !c.includes("Wild")) || playable[0];
        const idx = systemHand.indexOf(card);
        systemHand.splice(idx, 1);
        topCard = card;

        if(card.includes("Wild")){
            const colorCount = {};
            colors.forEach(c => colorCount[c] = 0);
            systemHand.forEach(c => {
                const col = c.split("_")[0];
                if(colorCount[col] !== undefined) colorCount[col]++;
            });
            currentColor = Object.keys(colorCount).reduce((a,b) => colorCount[a]>colorCount[b]?a:b);
            setMessage("🤖 System played Wild and chose " + currentColor);
        } else {
            currentColor = card.split("_")[0];
            setMessage("🤖 System played " + card.replace(".jpg",""));
        }

        if(card.includes("Skip") || card.includes("Reverse")){
            render();
            setMessage("🤖 System skipped your turn! System plays again.");
            setTimeout(aiMove, 1200);
            return;
        }

        if(card.includes("Draw_2")){
            for(let i=0;i<2;i++) { const c=drawCard(); if(c) userHand.push(c); }
            setMessage("🤖 System played Draw 2! You draw 2 cards.");
            render();
            setTimeout(aiMove, 1200);
            return;
        }

        if(card.includes("Wild_Draw_4")){
            for(let i=0;i<4;i++) { const c=drawCard(); if(c) userHand.push(c); }
            setMessage("🤖 System played Wild Draw 4! You draw 4 cards.");
            render();
            setTimeout(aiMove, 1200);
            return;
        }

    } else {
        const c = drawCard();
        if(c){
            systemHand.push(c);
            setMessage("🤖 System drew a card.");
        }
    }

    render();

    if(systemHand.length === 0){
        showWinner("system");
        return;
    }

    playerTurn = true;
}

function callUno(){
    if(userHand.length === 1){
        setMessage("🗣️ UNO! You called it!");
    } else {
        setMessage("⚠️ You can only call UNO with 1 card left!");
    }
}

function setMessage(msg){
    document.getElementById("message-box").innerText = msg;
}

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

function restartGame(){
    document.getElementById("popup-overlay").classList.remove("show");
    document.getElementById("hint-box").style.display = "none";
    document.getElementById("color-picker").style.display = "none";
    pendingWildCard = null;
    playerTurn = true;
    createDeck();
    shuffle();
    deal();
    setMessage("Game started! Your turn.");
    render();
}

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
                "Authorization": "Bearer """ + (API_KEY if API_KEY else "") + """"
            },
            body: JSON.stringify({
                model: "llama3-8b-8192",
                messages: [{
                    role: "user",
                    content: "You are an UNO expert. Top card: " + topCard.replace('.jpg','') + ". Current color: " + currentColor + ". My playable cards: " + playable.map(c=>c.replace('.jpg','')).join(", ") + ". System has " + systemHand.length + " cards. Which card should I play and why? Keep it under 2 sentences."
                }],
                max_tokens: 100
            })
        });
        const data = await response.json();
        hintBox.innerText = "💡 " + data.choices[0].message.content;
    } catch(e) {
        hintBox.innerText = "💡 Best card to play: " + playable[0].replace(".jpg","");
    }
}

createDeck();
shuffle();
deal();
render();
</script>

</body>
</html>
"""

st.components.v1.html(html_code, height=800, scrolling=False)
