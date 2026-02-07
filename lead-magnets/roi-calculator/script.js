// Industry-specific automation efficiency rates
const AUTOMATION_RATES = {
    restaurant: { adminReduction: 0.60, callCapture: 0.75, label: "Restaurant" },
    law: { adminReduction: 0.45, callCapture: 0.80, label: "Law Firm" },
    realestate: { adminReduction: 0.50, callCapture: 0.85, label: "Real Estate Agency" },
    dental: { adminReduction: 0.55, callCapture: 0.70, label: "Dental Office" },
    hvac: { adminReduction: 0.50, callCapture: 0.80, label: "HVAC/Trades Business" },
    accounting: { adminReduction: 0.55, callCapture: 0.70, label: "Accounting Firm" },
    other: { adminReduction: 0.45, callCapture: 0.70, label: "Business" },
};

function formatCurrency(amount) {
    return "$" + Math.round(amount).toLocaleString();
}

document.getElementById("roi-form").addEventListener("submit", function (e) {
    e.preventDefault();

    const industry = document.getElementById("industry").value;
    const hoursAdmin = parseFloat(document.getElementById("hours-admin").value);
    const hourlyRate = parseFloat(document.getElementById("hourly-rate").value);
    const missedCalls = parseFloat(document.getElementById("missed-calls").value);
    const avgDeal = parseFloat(document.getElementById("avg-deal").value);

    const rates = AUTOMATION_RATES[industry];

    // Monthly calculations (4.33 weeks/month)
    const weeksPerMonth = 4.33;
    const hoursSaved = hoursAdmin * rates.adminReduction * weeksPerMonth;
    const laborSavings = hoursSaved * hourlyRate;
    const callsRecovered = missedCalls * rates.callCapture * weeksPerMonth;
    const conversionRate = 0.15; // 15% of recovered calls convert
    const revenueRecovered = callsRecovered * conversionRate * avgDeal;
    const totalMonthly = laborSavings + revenueRecovered;
    const totalAnnual = totalMonthly * 12;

    document.getElementById("time-saved").textContent = Math.round(hoursSaved) + " hours";
    document.getElementById("labor-savings").textContent = formatCurrency(laborSavings);
    document.getElementById("revenue-recovered").textContent = formatCurrency(revenueRecovered);
    document.getElementById("total-impact").textContent = formatCurrency(totalMonthly);
    document.getElementById("annual-impact").textContent = formatCurrency(totalAnnual);
    document.getElementById("industry-name").textContent = rates.label;

    document.getElementById("results").classList.remove("hidden");
    document.getElementById("results").scrollIntoView({ behavior: "smooth" });
});

document.getElementById("cta-link").addEventListener("click", function (e) {
    e.preventDefault();
    document.getElementById("email-capture").classList.remove("hidden");
    document.getElementById("email-capture").scrollIntoView({ behavior: "smooth" });
});
