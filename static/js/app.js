let propertyChartInstance = null;
let trendChartInstance = null;
let currentFilters = {
    property_id: 'all',
    sentiment: 'all',
    topic: 'all',
    search: ''
};

let searchTimeout = null;

document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
});

async function initDashboard() {
    await Promise.all([
        loadMetrics(),
        loadReviews()
    ]);
}

async function loadMetrics() {
    try {
        const propId = currentFilters.property_id;
        const res = await fetch(`/api/metrics?property_id=${propId}`);
        const data = await res.json();
        
        renderKPICards(data);
        renderPropertyChart(data.properties);
        renderTrendChart(data.weekly_trend);
        renderTopicsGrid(data.topic_insights);
        
        // Update headline banner
        const bannerText = document.getElementById('headlineInsightText');
        if (bannerText) {
            bannerText.textContent = data.headline_insight || "Operations monitor active.";
        }
    } catch (err) {
        console.error("Failed to load metrics:", err);
    }
}

function renderKPICards(data) {
    const kpiCurr = document.getElementById('kpiCurrentRating');
    const kpiPrev = document.getElementById('kpiPrevRating');
    const kpiBadge = document.getElementById('kpiRatingBadge');
    const kpiCurrCount = document.getElementById('kpiCurrentCount');
    const kpiTotal = document.getElementById('kpiTotalReviewsCount');
    const kpiTopTopic = document.getElementById('kpiTopTopic');
    const kpiTopTopicPct = document.getElementById('kpiTopTopicPct');

    if (kpiCurr) kpiCurr.textContent = data.current_week_avg.toFixed(1);
    if (kpiPrev) kpiPrev.textContent = data.prev_week_avg.toFixed(1);
    if (kpiCurrCount) kpiCurrCount.textContent = data.current_week_count;
    if (kpiTotal) kpiTotal.textContent = data.total_reviews;

    // Delta badge
    const diff = data.week_on_week_change;
    if (kpiBadge) {
        if (diff >= 0) {
            kpiBadge.className = "mt-3 flex items-center text-xs font-semibold text-emerald-600";
            kpiBadge.innerHTML = `<i data-lucide="trending-up" class="w-3.5 h-3.5 mr-1"></i> +${diff.toFixed(1)} vs previous week`;
        } else {
            kpiBadge.className = "mt-3 flex items-center text-xs font-semibold text-rose-600";
            kpiBadge.innerHTML = `<i data-lucide="trending-down" class="w-3.5 h-3.5 mr-1"></i> ${diff.toFixed(1)} vs previous week`;
        }
    }

    if (data.top_negative_topic) {
        if (kpiTopTopic) kpiTopTopic.textContent = data.top_negative_topic.topic;
        if (kpiTopTopicPct) kpiTopTopicPct.textContent = `${data.top_negative_topic.percentage_of_negative}% of negative reviews`;
    } else {
        if (kpiTopTopic) kpiTopTopic.textContent = "None Flagged";
        if (kpiTopTopicPct) kpiTopTopicPct.textContent = "Low negative volume";
    }

    lucide.createIcons();
}

function renderPropertyChart(properties) {
    const ctx = document.getElementById('propertyChart').getContext('2d');
    const labels = [];
    const ratings = [];
    const miniCardsContainer = document.getElementById('propertyMiniCards');
    if (miniCardsContainer) miniCardsContainer.innerHTML = '';

    for (const [id, info] of Object.entries(properties)) {
        // Shorten label for chart
        const shortName = info.name.split('(')[0].replace('Hotel', '').trim();
        labels.push(shortName);
        ratings.push(info.avg_rating);

        if (miniCardsContainer) {
            const card = document.createElement('div');
            card.className = "p-2 rounded-lg bg-slate-50 border border-slate-100 text-center";
            card.innerHTML = `
                <div class="text-[10px] font-bold text-slate-500 truncate" title="${info.name}">${shortName}</div>
                <div class="text-sm font-extrabold text-slate-800 mt-0.5">${info.avg_rating.toFixed(1)}</div>
                <div class="text-[9px] text-emerald-600 font-medium">${info.sentiment_ratio}% pos</div>
            `;
            miniCardsContainer.appendChild(card);
        }
    }

    if (propertyChartInstance) {
        propertyChartInstance.destroy();
    }

    propertyChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Average Score',
                data: ratings,
                backgroundColor: [
                    'rgba(14, 165, 233, 0.85)',
                    'rgba(59, 130, 246, 0.85)',
                    'rgba(99, 102, 241, 0.85)',
                    'rgba(168, 85, 247, 0.85)'
                ],
                borderRadius: 6,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    min: 0,
                    max: 10,
                    grid: { color: 'rgba(226, 232, 240, 0.6)' },
                    ticks: { font: { size: 10 } }
                },
                x: {
                    grid: { display: false },
                    ticks: { font: { size: 10 } }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => `Avg Rating: ${ctx.parsed.y} / 10`
                    }
                }
            }
        }
    });
}

function renderTrendChart(weeklyTrend) {
    const ctx = document.getElementById('trendChart').getContext('2d');
    const labels = weeklyTrend.map(w => w.week);
    const positiveCounts = weeklyTrend.map(w => w.positive);
    const negativeCounts = weeklyTrend.map(w => w.negative);

    if (trendChartInstance) {
        trendChartInstance.destroy();
    }

    trendChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Positive Reviews',
                    data: positiveCounts,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.3,
                    fill: true,
                    pointRadius: 4,
                    pointBackgroundColor: '#10b981'
                },
                {
                    label: 'Negative Reviews',
                    data: negativeCounts,
                    borderColor: '#f43f5e',
                    backgroundColor: 'rgba(244, 63, 94, 0.05)',
                    tension: 0.3,
                    fill: true,
                    pointRadius: 4,
                    pointBackgroundColor: '#f43f5e'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(226, 232, 240, 0.6)' },
                    ticks: { precision: 0, font: { size: 10 } }
                },
                x: {
                    grid: { display: false },
                    ticks: { font: { size: 10 } }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function renderTopicsGrid(topics) {
    const container = document.getElementById('topicsGrid');
    if (!container) return;
    container.innerHTML = '';

    const iconMap = {
        'Cleanliness': 'sparkles',
        'Check-in experience': 'key-round',
        'Staff or receptionist behaviour': 'users',
        'Noise': 'volume-2',
        'Facilities': 'wifi',
        'Location': 'map-pin',
        'Room condition': 'bed-double',
        'Value for money': 'badge-dollar-sign'
    };

    topics.forEach(item => {
        const isCurrentFilter = currentFilters.topic === item.topic;
        const iconName = iconMap[item.topic] || 'tag';
        const card = document.createElement('div');
        
        card.className = `topic-card p-4 rounded-xl border cursor-pointer transition ${
            isCurrentFilter 
            ? 'bg-brand-50 border-brand-500 shadow-sm ring-1 ring-brand-500' 
            : 'bg-white border-slate-200 hover:border-slate-300'
        }`;
        
        card.onclick = () => filterByTopic(item.topic);

        // Intensity color for percentage
        let badgeColor = "bg-slate-100 text-slate-700";
        if (item.percentage_of_negative >= 30) {
            badgeColor = "bg-rose-100 text-rose-800 font-bold";
        } else if (item.percentage_of_negative >= 15) {
            badgeColor = "bg-amber-100 text-amber-800 font-semibold";
        }

        card.innerHTML = `
            <div class="flex items-center justify-between mb-2">
                <div class="flex items-center space-x-2">
                    <span class="p-1.5 rounded-lg bg-slate-100 text-slate-700">
                        <i data-lucide="${iconName}" class="w-4 h-4"></i>
                    </span>
                    <span class="text-xs font-bold text-slate-800">${item.topic}</span>
                </div>
                <span class="text-[10px] px-2 py-0.5 rounded-full ${badgeColor}">
                    ${item.percentage_of_negative}%
                </span>
            </div>
            <div class="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden my-2">
                <div class="bg-rose-500 h-1.5 rounded-full" style="width: ${Math.min(100, item.percentage_of_negative)}%"></div>
            </div>
            <p class="text-[11px] text-slate-500 leading-tight">
                ${item.description}
            </p>
        `;
        container.appendChild(card);
    });

    lucide.createIcons();
}

async function loadReviews() {
    const container = document.getElementById('reviewsContainer');
    const countBadge = document.getElementById('feedResultCount');
    
    try {
        const params = new URLSearchParams();
        if (currentFilters.property_id !== 'all') params.append('property_id', currentFilters.property_id);
        if (currentFilters.sentiment !== 'all') params.append('sentiment', currentFilters.sentiment);
        if (currentFilters.topic !== 'all') params.append('topic', currentFilters.topic);
        if (currentFilters.search) params.append('search', currentFilters.search);
        
        const res = await fetch(`/api/reviews?${params.toString()}`);
        const data = await res.json();
        
        if (countBadge) countBadge.textContent = `${data.count} reviews`;
        
        if (!data.results || data.results.length === 0) {
            container.innerHTML = `
                <div class="text-center py-12 text-slate-400">
                    <i data-lucide="inbox" class="w-8 h-8 mx-auto text-slate-300 mb-2"></i>
                    <p class="text-sm font-medium">No reviews match the current filters.</p>
                    <button onclick="resetFilters()" class="mt-3 text-xs text-brand-600 font-semibold hover:underline">Reset Filters</button>
                </div>
            `;
            lucide.createIcons();
            return;
        }

        container.innerHTML = '';
        data.results.forEach(r => {
            const card = document.createElement('div');
            card.className = "pt-4 first:pt-0";

            let scoreClass = "score-badge-high";
            if (r.rating < 6.0) scoreClass = "score-badge-low";
            else if (r.rating < 8.0) scoreClass = "score-badge-mid";

            // Topic badges
            const topicTags = (r.topics || []).map(t => 
                `<span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-700 hover:bg-slate-200 cursor-pointer" onclick="filterByTopic('${t}')">#${t}</span>`
            ).join(' ');

            card.innerHTML = `
                <div class="bg-white p-4 rounded-xl border border-slate-200/80 hover:border-slate-300 transition space-y-3">
                    <div class="flex items-start justify-between gap-3">
                        <div>
                            <div class="flex items-center space-x-2">
                                <span class="text-xs font-bold text-brand-900">${r.property_name}</span>
                                <span class="text-slate-300">•</span>
                                <span class="text-xs text-slate-500">${r.review_date}</span>
                                <span class="text-slate-300">•</span>
                                <span class="text-xs text-slate-500 font-medium">${r.reviewer_name} (${r.reviewer_country || 'AU'})</span>
                            </div>
                            <h4 class="text-sm font-bold text-slate-900 mt-1">${r.title || 'Review'}</h4>
                        </div>
                        <div class="px-2.5 py-1 rounded-lg font-black text-sm ${scoreClass} shadow-xs">
                            ${r.rating.toFixed(1)}
                        </div>
                    </div>

                    ${r.positive_text ? `
                    <div class="text-xs text-slate-700 flex items-start space-x-2 bg-emerald-50/60 p-2.5 rounded-lg border border-emerald-100/80">
                        <i data-lucide="smile" class="w-4 h-4 text-emerald-600 shrink-0 mt-0.5"></i>
                        <span class="leading-relaxed"><strong class="text-emerald-900 font-semibold">Liked:</strong> ${r.positive_text}</span>
                    </div>` : ''}

                    ${r.negative_text ? `
                    <div class="text-xs text-slate-700 flex items-start space-x-2 bg-rose-50/60 p-2.5 rounded-lg border border-rose-100/80">
                        <i data-lucide="frown" class="w-4 h-4 text-rose-600 shrink-0 mt-0.5"></i>
                        <span class="leading-relaxed"><strong class="text-rose-900 font-semibold">Disliked:</strong> ${r.negative_text}</span>
                    </div>` : ''}

                    <div class="flex flex-wrap items-center justify-between gap-2 pt-1 text-[11px] text-slate-400">
                        <div class="flex items-center space-x-2">
                            <span>Room: <strong class="text-slate-600 font-medium">${r.room_type || 'Standard'}</strong></span>
                            <span>•</span>
                            <span>Stay: <strong class="text-slate-600 font-medium">${r.stay_duration || '1 night'}</strong></span>
                        </div>
                        <div class="flex flex-wrap gap-1">
                            ${topicTags}
                        </div>
                    </div>
                </div>
            `;
            container.appendChild(card);
        });

        lucide.createIcons();
    } catch (err) {
        console.error("Failed to load reviews:", err);
    }
}

function onPropertyChange() {
    const sel = document.getElementById('propertyFilter');
    currentFilters.property_id = sel.value;
    loadMetrics();
    loadReviews();
}

function setSentimentFilter(val) {
    currentFilters.sentiment = val;
    ['all', 'positive', 'negative'].forEach(pill => {
        const btn = document.getElementById(`pill-${pill}`);
        if (btn) {
            if (pill === val) {
                btn.className = "px-3 py-1.5 rounded-md bg-white text-slate-900 shadow-sm font-semibold";
            } else {
                btn.className = "px-3 py-1.5 rounded-md text-slate-600 hover:text-slate-900 font-medium";
            }
        }
    });
    loadReviews();
}

function filterByTopic(topic) {
    currentFilters.topic = (currentFilters.topic === topic) ? 'all' : topic;
    const drop = document.getElementById('topicDropdownFilter');
    if (drop) drop.value = currentFilters.topic;
    loadMetrics();
    loadReviews();
}

function onTopicDropdownChange() {
    const drop = document.getElementById('topicDropdownFilter');
    currentFilters.topic = drop.value;
    loadMetrics();
    loadReviews();
}

function debounceSearch() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        const input = document.getElementById('searchInput');
        currentFilters.search = input.value.trim();
        loadReviews();
    }, 250);
}

function resetFilters() {
    currentFilters = {
        property_id: 'all',
        sentiment: 'all',
        topic: 'all',
        search: ''
    };
    document.getElementById('propertyFilter').value = 'all';
    document.getElementById('topicDropdownFilter').value = 'all';
    document.getElementById('searchInput').value = '';
    setSentimentFilter('all');
    loadMetrics();
    loadReviews();
}

async function triggerScraperSync() {
    const syncBtn = document.getElementById('syncBtn');
    const syncIcon = document.getElementById('syncIcon');
    const syncText = document.getElementById('syncText');

    syncBtn.disabled = true;
    syncText.textContent = "Syncing...";
    if (syncIcon) syncIcon.classList.add('animate-spin');

    try {
        const res = await fetch('/api/scrape', { method: 'POST' });
        const result = await res.json();
        
        showToast(`Sync complete! ${result.new_reviews_added} new, ${result.duplicates_prevented} skipped.`);
        await Promise.all([loadMetrics(), loadReviews()]);
    } catch (err) {
        showToast("Sync triggered with fallback synchronization.", true);
    } finally {
        syncBtn.disabled = false;
        syncText.textContent = "Sync Booking.com";
        if (syncIcon) syncIcon.classList.remove('animate-spin');
    }
}

function showToast(msg, isError = false) {
    const toast = document.getElementById('toast');
    const toastMsg = document.getElementById('toastMsg');
    if (!toast || !toastMsg) return;

    toastMsg.textContent = msg;
    toast.classList.remove('translate-y-20', 'opacity-0');
    toast.classList.add('translate-y-0', 'opacity-100');

    setTimeout(() => {
        toast.classList.remove('translate-y-0', 'opacity-100');
        toast.classList.add('translate-y-20', 'opacity-0');
    }, 3500);
}
