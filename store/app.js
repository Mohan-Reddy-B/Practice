const pieces = [
  {
    id: "charter-coat",
    name: "The Charter Coat",
    fabric: "Charcoal wool",
    price: 28500,
    image: "media/ashford-hero-coat.jpg",
    feature: true,
    note: "A single-breasted overcoat in dense charcoal wool. Half canvas, horn buttons, and a collar that sits close to the neck.",
  },
  {
    id: "meridian-shirt",
    name: "The Meridian Shirt",
    fabric: "Ivory oxford",
    price: 6800,
    image: "media/ashford-oxford.jpg",
    note: "An ivory oxford with a soft collar, a clean placket, and mother-of-pearl buttons. Cut with room through the shoulder.",
  },
  {
    id: "harbor-knit",
    name: "The Harbor Knit",
    fabric: "Navy merino",
    price: 9400,
    image: "media/ashford-knit.jpg",
    note: "A fully fashioned merino crew in deep navy. Ribbed hem and cuffs, light enough to wear under the coat.",
  },
  {
    id: "ledger-jacket",
    name: "The Ledger Jacket",
    fabric: "Camel suede",
    price: 22000,
    image: "media/ashford-suede.jpg",
    note: "An unlined camel suede jacket with three buttons. It takes a mark, which is the point of suede.",
  },
  {
    id: "night-linen",
    name: "The Night Linen",
    fabric: "Black linen",
    price: 16500,
    image: "media/ashford-linen.jpg",
    note: "An unstructured black linen blazer. Unpadded shoulder, patch pockets, meant for warm evenings.",
  },
];

const sizes = ["S", "M", "L", "XL"];
const money = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

const grid = document.querySelector("#product-grid");
const productDrawer = document.querySelector("#product-drawer");
const bagDrawer = document.querySelector("#bag-drawer");
const bagCount = document.querySelector("#bag-count");
const bagLines = document.querySelector("#bag-lines");
const bagTotal = document.querySelector("#bag-total");
const sizeRow = document.querySelector("#size-row");
const sizeError = document.querySelector("#size-error");
const reserveNote = document.querySelector("#reserve-note");

let bag = loadBag();
let activeId = null;
let activeSize = null;

function loadBag() {
  try {
    const saved = JSON.parse(localStorage.getItem("ashford-bag") || "[]");
    return Array.isArray(saved) ? saved : [];
  } catch {
    return [];
  }
}

function saveBag() {
  localStorage.setItem("ashford-bag", JSON.stringify(bag));
  renderBag();
}

function findPiece(id) {
  return pieces.find((piece) => piece.id === id);
}

function renderGrid() {
  grid.innerHTML = "";
  pieces.forEach((piece) => {
    const card = document.createElement("button");
    card.type = "button";
    card.className = piece.feature ? "card feature" : "card";
    card.innerHTML = `
      <img src="${piece.image}" alt="${piece.name}" />
      <span class="card-name">${piece.name}</span>
      <span class="card-meta"><span>${piece.fabric}</span><span>${money.format(piece.price)}</span></span>
    `;
    card.addEventListener("click", () => openProduct(piece.id));
    grid.appendChild(card);
  });
}

function openProduct(id) {
  const piece = findPiece(id);
  activeId = id;
  activeSize = null;
  sizeError.hidden = true;
  document.querySelector("#product-image").src = piece.image;
  document.querySelector("#product-image").alt = piece.name;
  document.querySelector("#product-fabric").textContent = piece.fabric;
  document.querySelector("#product-title").textContent = piece.name;
  document.querySelector("#product-price").textContent = money.format(piece.price);
  document.querySelector("#product-note").textContent = piece.note;
  sizeRow.innerHTML = "";
  sizes.forEach((size) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = size;
    button.setAttribute("aria-pressed", "false");
    button.addEventListener("click", () => {
      activeSize = size;
      sizeError.hidden = true;
      sizeRow.querySelectorAll("button").forEach((other) => {
        other.setAttribute("aria-pressed", String(other === button));
      });
    });
    sizeRow.appendChild(button);
  });
  document.querySelector("#add-to-bag").textContent = "Add to bag";
  productDrawer.hidden = false;
  document.body.style.overflow = "hidden";
}

function openBag() {
  reserveNote.hidden = true;
  bagDrawer.hidden = false;
  document.body.style.overflow = "hidden";
}

function closeDrawers() {
  productDrawer.hidden = true;
  bagDrawer.hidden = true;
  document.body.style.overflow = "";
}

function addToBag() {
  if (!activeSize) {
    sizeError.hidden = false;
    return;
  }
  const existing = bag.find((line) => line.id === activeId && line.size === activeSize);
  if (existing) existing.qty += 1;
  else bag.push({ id: activeId, size: activeSize, qty: 1 });
  saveBag();
  const button = document.querySelector("#add-to-bag");
  button.textContent = "Added";
  window.setTimeout(() => {
    closeDrawers();
    openBag();
  }, 280);
}

function renderBag() {
  const count = bag.reduce((sum, line) => sum + line.qty, 0);
  bagCount.textContent = String(count);
  if (!bag.length) {
    bagLines.innerHTML = '<p class="bag-empty">The bag is empty. The edit is still on the rail.</p>';
    bagTotal.textContent = "";
    return;
  }
  bagLines.innerHTML = "";
  let total = 0;
  bag.forEach((line, index) => {
    const piece = findPiece(line.id);
    total += piece.price * line.qty;
    const row = document.createElement("div");
    row.className = "bag-line";
    row.innerHTML = `
      <img src="${piece.image}" alt="" />
      <div>
        <p>${piece.name}</p>
        <p>Size ${line.size}</p>
        <div class="qty">
          <button type="button" data-qty="-1" data-index="${index}" aria-label="Decrease quantity">−</button>
          <span>${line.qty}</span>
          <button type="button" data-qty="1" data-index="${index}" aria-label="Increase quantity">+</button>
        </div>
      </div>
      <div>
        <p>${money.format(piece.price * line.qty)}</p>
        <button class="remove" type="button" data-remove="${index}">Remove</button>
      </div>
    `;
    bagLines.appendChild(row);
  });
  bagTotal.innerHTML = `<span>Total</span><span>${money.format(total)}</span>`;
}

document.querySelector("#open-bag").addEventListener("click", openBag);
document.querySelector("#add-to-bag").addEventListener("click", addToBag);
document.querySelector("#reserve").addEventListener("click", () => {
  if (!bag.length) return;
  saveBag();
  reserveNote.hidden = false;
});

document.body.addEventListener("click", (event) => {
  const closer = event.target.closest("[data-close]");
  if (closer) closeDrawers();
  const qty = event.target.closest("[data-qty]");
  if (qty) {
    const index = Number(qty.dataset.index);
    bag[index].qty += Number(qty.dataset.qty);
    if (bag[index].qty <= 0) bag.splice(index, 1);
    saveBag();
  }
  const remove = event.target.closest("[data-remove]");
  if (remove) {
    bag.splice(Number(remove.dataset.remove), 1);
    saveBag();
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closeDrawers();
});

document.querySelector('a[href="#film"]').addEventListener("click", () => {
  const film = document.querySelector("#wide-film");
  window.setTimeout(() => {
    film.play().catch(() => {});
  }, 350);
});

renderGrid();
renderBag();
