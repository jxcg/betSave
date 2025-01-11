function addRow() {
    const table = document.getElementById('bettingTable').getElementsByTagName('tbody')[0];
    const newRow = document.createElement('tr');

    const cols = [
        '<input type="date">',
        '<input type="text" placeholder="Bookmaker">',
        '<input type="text" placeholder="Event">',
        createButtonGroup(), // Call the function to create the button group
        '<input type="number" step="0.01" placeholder="Stake" class="stake">',
        '<input type="number" step="0.01" placeholder="Odds (Back)">',
        '<input type="number" step="0.01" placeholder="Odds (Lay)">',
        '<input type="number" step="0.01" placeholder="Lay Liability">',
        '<input type="text" placeholder="Exchange Used">',
        '<input type="text" placeholder="Outcome">',
        '<input type="number" step="0.01" placeholder="Profit/Loss (Bookmaker)" class="profit-bookmaker">',
        '<input type="number" step="0.01" placeholder="Profit/Loss (Exchange)" class="profit-exchange">',
        '<input type="number" step="0.01" placeholder="Net Profit/Loss" readonly class="net-profit">',
        '<input type="number" step="0.01" placeholder="Cumulative Profit" readonly class="cumulative-profit">'
    ];

    for (const col of cols) {
        const td = document.createElement('td');
        if (typeof col === "string") {
            td.innerHTML = col;
        } else {
            td.appendChild(col); // Append button group directly as a DOM element
        }
        newRow.appendChild(td);
    }

    table.appendChild(newRow);
    updateEventListeners();
}

function createButtonGroup() {
    const container = document.createElement('div');
    container.className = 'button-group-container';

    const buttonValues = ["Free Bet", "Qualifying Bet", "Arb Bet"];
    const outcomeValues = ["Win", "Lose", "Void", "Draw"];
    buttonValues.forEach(value => {
        const button = document.createElement('button');
        button.textContent = value;
        button.type = 'button';
        button.className = 'bet-type-button';
        button.addEventListener('click', () => {
            const buttons = container.querySelectorAll('button');
            buttons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            button.setAttribute('data-selected', value);
        });
        container.appendChild(button);
    });

    return container;
}

function updateEventListeners() {
    const rows = document.querySelectorAll('#bettingTable tbody tr');
    rows.forEach(row => {
        const profitBookmaker = row.querySelector('.profit-bookmaker');
        const profitExchange = row.querySelector('.profit-exchange');
        const netProfit = row.querySelector('.net-profit');
        const cumulativeProfit = row.querySelector('.cumulative-profit');

        if (profitBookmaker && profitExchange) {
            const inputs = [profitBookmaker, profitExchange];
            inputs.forEach(input => {
                input.addEventListener('input', () => {
                    calculateNetProfit(row);
                    calculateCumulativeProfit();
                });
            });
        }
    });
}

function calculateNetProfit(row) {
    const profitBookmaker = parseFloat(row.querySelector('.profit-bookmaker').value) || 0;
    const profitExchange = parseFloat(row.querySelector('.profit-exchange').value) || 0;
    const netProfit = row.querySelector('.net-profit');

    netProfit.value = (profitBookmaker + profitExchange).toFixed(2);
}

function calculateCumulativeProfit() {
    const rows = document.querySelectorAll('#bettingTable tbody tr');
    let cumulative = 0;

    rows.forEach(row => {
        const netProfit = parseFloat(row.querySelector('.net-profit').value) || 0;
        const cumulativeProfit = row.querySelector('.cumulative-profit');

        cumulative += netProfit;
        cumulativeProfit.value = cumulative.toFixed(2);
    });
}

// Initialize the event listeners on page load
updateEventListeners();
