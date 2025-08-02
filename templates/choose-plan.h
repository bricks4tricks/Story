<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Logic and Stories | Choose Plan</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Pacifico&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Nunito', sans-serif; }
        .font-pacifico { font-family: 'Pacifico', cursive; }
        .gradient-text { background: linear-gradient(to right, #fde047, #fb923c); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .glow-button { box-shadow: 0 0 15px rgba(253,224,71,0.5), 0 0 5px rgba(251,146,60,0.4); }
    </style>
</head>
<body class="bg-slate-900 text-gray-200">
    <header class="bg-slate-900/80 backdrop-blur-sm sticky top-0 z-50 border-b border-slate-800">
        <nav class="container mx-auto px-6 py-4 flex justify-between items-center">
            <a href="/" class="text-3xl font-pacifico gradient-text pb-1 leading-normal">Logic and Stories</a>
        </nav>
    </header>
    <main class="py-12">
        <div class="container mx-auto px-6">
            <div class="text-center mb-12">
                <h2 class="text-3xl md:text-4xl font-bold text-white">Choose Your Adventure Plan</h2>
                <p class="text-gray-400 mt-2">Simple, transparent pricing. Cancel anytime.</p>
                <div id="message" class="text-center mt-6"></div>
            </div>
            <div class="flex flex-col lg:flex-row justify-center items-center gap-8">
                <div class="w-full lg:w-1/3 bg-slate-800 p-8 rounded-2xl border border-slate-700">
                    <h3 class="text-2xl font-bold text-white text-center">Monthly</h3>
                    <p class="text-center text-gray-400 mt-2">Perfect for trying things out.</p>
                    <p class="text-5xl font-extrabold text-white text-center my-6">$12<span class="text-lg font-medium text-gray-400">/mo</span></p>
                    <ul class="space-y-4 text-gray-300">
                        <li class="flex items-center"><svg class="w-5 h-5 text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>Access to all stories & themes</li>
                        <li class="flex items-center"><svg class="w-5 h-5 text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>1 student profile</li>
                        <li class="flex items-center"><svg class="w-5 h-5 text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>New stories monthly</li>
                    </ul>
                    <button class="plan-select glow-button w-full mt-8 bg-gray-700 text-white font-bold py-3 px-6 rounded-full hover:bg-gray-600 transition-colors"
                            data-plan="Monthly">
                        Choose Plan
                    </button>
                </div>
                <div class="w-full lg:w-1/3 bg-slate-800 p-8 rounded-2xl border-2 border-yellow-400 relative transform lg:scale-110">
                    <div class="absolute top-0 -translate-y-1/2 left-1/2 -translate-x-1/2">
                        <span class="bg-yellow-400 text-slate-900 text-sm font-bold px-4 py-1 rounded-full">BEST VALUE</span>
                    </div>
                    <h3 class="text-2xl font-bold text-white text-center">Annual</h3>
                    <p class="text-center text-gray-400 mt-2">Save 25% and learn all year.</p>
                    <p class="text-5xl font-extrabold text-white text-center my-6">$9<span class="text-lg font-medium text-gray-400">/mo</span></p>
                    <ul class="space-y-4 text-gray-300">
                        <li class="flex items-center"><svg class="w-5 h-5 text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>Access to all stories & themes</li>
                        <li class="flex items-center"><svg class="w-5 h-5 text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>Up to 3 student profiles</li>
                        <li class="flex items-center"><svg class="w-5 h-5 text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>New stories monthly</li>
                        <li class="flex items-center"><svg class="w-5 h-5 text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>Early access to new content</li>
                    </ul>
                    <button class="plan-select glow-button w-full mt-8 bg-yellow-400 text-slate-900 font-bold py-3 px-6 rounded-full hover:bg-yellow-300 transition-all transform hover:scale-105"
                            data-plan="Annual">
                        Choose Plan
                    </button>
                </div>
                <div class="w-full lg:w-1/3 bg-slate-800 p-8 rounded-2xl border border-slate-700">
                    <h3 class="text-2xl font-bold text-white text-center">Family</h3>
                    <p class="text-center text-gray-400 mt-2">For the whole adventuring crew.</p>
                    <p class="text-5xl font-extrabold text-white text-center my-6">$18<span class="text-lg font-medium text-gray-400">/mo</span></p>
                    <ul class="space-y-4 text-gray-300">
                        <li class="flex items-center"><svg class="w-5 h-5 text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>Access to all stories & themes</li>
                        <li class="flex items-center"><svg class="w-5 h-5 text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>Up to 5 student profiles</li>
                        <li class="flex items-center"><svg class="w-5 h-5 text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>Priority support</li>
                    </ul>
                    <button class="plan-select glow-button w-full mt-8 bg-gray-700 text-white font-bold py-3 px-6 rounded-full hover:bg-gray-600 transition-colors"
                            data-plan="Family">
                        Choose Plan
                    </button>
                </div>
            </div>
        </div>
    </main>
    <div id="flag-modal" class="modal modal-hidden fixed inset-0 bg-black bg-opacity-70 z-50 flex justify-center items-center opacity-0">
        <div class="modal-content bg-slate-800 rounded-2xl p-8 max-w-md w-full mx-4 relative scale-95">
            <button id="close-flag-modal" class="absolute top-4 right-4 text-gray-400 hover:text-white">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
            <h2 class="text-2xl font-bold text-white mb-4">Report Issue</h2>
            <textarea id="flag-reason" class="w-full h-32 bg-slate-700 text-gray-200 p-2 rounded-md mb-4" placeholder="Describe the issue (optional)"></textarea>
            <button id="submit-flag-btn" class="bg-yellow-400 text-slate-900 font-bold py-2 px-6 rounded-full hover:bg-yellow-300 w-full">Submit</button>
        </div>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const urlParams = new URLSearchParams(window.location.search);
            const userId = urlParams.get('userId');
            const messageDiv = document.getElementById('message');
            const planButtons = document.querySelectorAll('.plan-select');
            // Start with a neutral message state.
            messageDiv.textContent = '';
            messageDiv.className = 'text-center text-gray-400 mt-6';

            // If the userId is missing, display an error and prevent interaction.
            if (!userId) {
                messageDiv.className = 'text-center text-red-400 mt-6';
                messageDiv.textContent = 'Error: missing user information. Please sign up again.';
                planButtons.forEach(btn => btn.disabled = true);
                // Redirect back to signup after a short delay so the user can recover.
                setTimeout(() => { window.location.href = '/signup.h'; }, 3000);
                return;
            }

            // Enable buttons when a valid user is present.
            planButtons.forEach(btn => btn.disabled = false);

            planButtons.forEach(button => {
                button.addEventListener('click', async () => {
                    const plan = button.dataset.plan;
                    // Disable buttons while the request is in flight to avoid duplicate submissions
                    planButtons.forEach(btn => btn.disabled = true);
                    messageDiv.className = 'text-center text-gray-400 mt-6';
                    messageDiv.textContent = 'Updating plan...';
                    try {
                        const response = await fetch('/api/select-plan', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ userId, plan })
                        });
                        // ``response.json`` may throw if the server does not return JSON
                        const result = await response.json().catch(() => ({}));
                        if (response.ok && result.status === 'success') {
                            messageDiv.className = 'text-center text-green-400 mt-6';
                            messageDiv.textContent = 'Plan selected! Redirecting...';
                            setTimeout(() => { window.location.href = '/'; }, 2000);
                        } else {
                            messageDiv.className = 'text-center text-red-400 mt-6';
                            messageDiv.textContent = result.message || 'An error occurred.';
                            planButtons.forEach(btn => btn.disabled = false);
                        }
                    } catch (err) {
                        console.error('Could not update plan', err);
                        messageDiv.className = 'text-center text-red-400 mt-6';
                        messageDiv.textContent = 'Could not update plan.';
                        planButtons.forEach(btn => btn.disabled = false);
                    }
                });
            });
        });
    </script>
    <script src="/static/js/flagModal.js"></script>
    <script src="/static/js/flagErrorButton.js"></script>
</body>
</html>
