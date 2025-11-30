document.addEventListener('DOMContentLoaded', () => {
    // --- State Management ---
    const state = {
        user: null,
        currentFile: null,
        currentFileName: '',
        flashcards: [],
        currentIndex: 0,
        selectedDifficulty: 'medium',
        selectedCardCount: 20
    };

    // --- Elements ---
    const authModal = document.getElementById('auth-modal');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const showRegisterBtn = document.getElementById('show-register');
    const showLoginBtn = document.getElementById('show-login');
    const loginBtn = document.getElementById('login-btn');
    const registerBtn = document.getElementById('register-btn');
    const logoutBtn = document.getElementById('logout-btn');
    const authError = document.getElementById('auth-error');
    const mainApp = document.getElementById('main-app');

    // Completion Modal
    const completionModal = document.getElementById('completion-modal');
    const completionXp = document.getElementById('completion-xp');
    const completionTotalXp = document.getElementById('completion-total-xp');
    const completionLevel = document.getElementById('completion-level');
    const completionCards = document.getElementById('completion-cards');
    const completionStreak = document.getElementById('completion-streak');
    const levelUpBadge = document.getElementById('level-up-badge');
    const newLevelSpan = document.getElementById('new-level');
    const uploadNewBtn = document.getElementById('upload-new-btn');
    const backToDashboardBtn = document.getElementById('back-to-dashboard-btn');

    const views = document.querySelectorAll('.view');
    const navLinks = document.querySelectorAll('.nav-links li');
    const themeToggle = document.getElementById('theme-toggle');

    // Dashboard Elements
    const userNameDisplay = document.getElementById('user-name-display');
    const streakDisplay = document.getElementById('streak-display');
    const xpDisplay = document.getElementById('xp-display');
    const levelDisplay = document.getElementById('level-display');
    const decksCount = document.getElementById('decks-count');
    const cardsMastered = document.getElementById('cards-mastered');
    const quickCreateBtn = document.getElementById('quick-create-btn');

    // Upload Elements
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const generateBtn = document.getElementById('generate-btn');
    const difficultyOptions = document.querySelectorAll('.difficulty-option');
    const cardCountSlider = document.getElementById('card-count-slider');
    const cardCountDisplay = document.getElementById('card-count-display');

    // Study Elements
    const flashcard = document.getElementById('flashcard');
    const cardQuestion = document.getElementById('card-question');
    const cardAnswer = document.getElementById('card-answer');
    const cardExplanation = document.getElementById('card-explanation');
    const cardTypeBadge = document.getElementById('card-type');
    const mcqOptions = document.getElementById('mcq-options');
    const currentCardNum = document.getElementById('current-card-num');
    const totalCardsNum = document.getElementById('total-cards-num');
    const studyProgress = document.getElementById('study-progress');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const flipBtn = document.getElementById('flip-btn');
    const backToDashBtn = document.querySelector('.back-to-dash');

    // Profile Elements
    const profileUsername = document.getElementById('profile-username');
    const profileEmail = document.getElementById('profile-email');
    const profileJoinDate = document.getElementById('profile-join-date');
    const profileXp = document.getElementById('profile-xp');
    const profileLevel = document.getElementById('profile-level');
    const profileStreak = document.getElementById('profile-streak');
    const profileDecks = document.getElementById('profile-decks');

    // --- Initialization ---
    checkAuth();
    setupAuth();
    setupNavigation();
    setupTheme();
    setupUpload();
    setupStudyControls();
    setupCustomCursor();
    setupCompletionModal();
    setupLeaderboard();

    // --- Authentication ---
    function checkAuth() {
        fetch('/api/auth/me')
            .then(res => res.json())
            .then(user => {
                if (user.error) {
                    showAuthModal();
                } else {
                    state.user = user;
                    hideAuthModal();
                    updateUserUI(user);
                }
            })
            .catch(() => showAuthModal());
    }

    function setupAuth() {
        showRegisterBtn.addEventListener('click', () => {
            loginForm.classList.add('hidden');
            registerForm.classList.remove('hidden');
            authError.classList.add('hidden');
        });

        showLoginBtn.addEventListener('click', () => {
            registerForm.classList.add('hidden');
            loginForm.classList.remove('hidden');
            authError.classList.add('hidden');
        });

        loginBtn.addEventListener('click', handleLogin);
        registerBtn.addEventListener('click', handleRegister);
        logoutBtn.addEventListener('click', handleLogout);
    }

    function handleLogin() {
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        })
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    showError(data.error);
                } else {
                    state.user = data;
                    hideAuthModal();
                    updateUserUI(data);
                }
            })
            .catch(err => showError('Login failed'));
    }

    function handleRegister() {
        const username = document.getElementById('register-username').value;
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;

        fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        })
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    showError(data.error);
                } else {
                    state.user = data;
                    hideAuthModal();
                    updateUserUI(data);
                }
            })
            .catch(err => showError('Registration failed'));
    }

    function handleLogout() {
        fetch('/api/auth/logout', { method: 'POST' })
            .then(() => {
                state.user = null;
                showAuthModal();
            });
    }

    function showAuthModal() {
        authModal.classList.remove('hidden');
        mainApp.classList.add('hidden');
    }

    function hideAuthModal() {
        authModal.classList.add('hidden');
        mainApp.classList.remove('hidden');
    }

    function showError(message) {
        authError.textContent = message;
        authError.classList.remove('hidden');
    }

    function updateUserUI(user) {
        userNameDisplay.textContent = user.username;
        streakDisplay.textContent = user.streak || 0;
        xpDisplay.textContent = user.total_xp || 0;
        levelDisplay.textContent = user.current_level || 1;
        decksCount.textContent = user.decks_created || 0;
        cardsMastered.textContent = user.cards_mastered || 0;

        // Profile
        profileUsername.textContent = user.username;
        profileEmail.textContent = user.email;
        profileJoinDate.textContent = new Date(user.created_at).toLocaleDateString();
        profileXp.textContent = user.total_xp || 0;
        profileLevel.textContent = user.current_level || 1;
        profileStreak.textContent = (user.streak || 0) + ' 🔥';
        profileDecks.textContent = user.decks_completed || 0;
    }

    function refreshUserData() {
        fetch('/api/auth/me')
            .then(res => res.json())
            .then(user => {
                if (!user.error) {
                    state.user = user;
                    updateUserUI(user);
                }
            });
    }

    // --- Navigation ---
    function setupNavigation() {
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                const viewName = link.getAttribute('data-view');
                switchView(viewName);
            });
        });

        quickCreateBtn.addEventListener('click', () => switchView('upload'));
        backToDashBtn.addEventListener('click', () => switchView('dashboard'));
    }

    function switchView(viewName) {
        navLinks.forEach(link => {
            link.classList.toggle('active', link.getAttribute('data-view') === viewName);
        });

        views.forEach(view => {
            view.classList.remove('active-view');
            if (view.id === `view-${viewName}`) {
                view.classList.add('active-view');
            }
        });
    }

    // --- Theme ---
    function setupTheme() {
        themeToggle.addEventListener('click', () => {
            const body = document.body;
            const icon = themeToggle.querySelector('i');
            if (body.getAttribute('data-theme') === 'light') {
                body.setAttribute('data-theme', 'dark');
                icon.classList.replace('fa-sun', 'fa-moon');
            } else {
                body.setAttribute('data-theme', 'light');
                icon.classList.replace('fa-moon', 'fa-sun');
            }
        });
    }

    // --- Custom Cursor ---
    function setupCustomCursor() {
        const dot = document.querySelector('.cursor-dot');
        const outline = document.querySelector('.cursor-outline');

        window.addEventListener('mousemove', (e) => {
            const posX = e.clientX;
            const posY = e.clientY;

            dot.style.left = `${posX}px`;
            dot.style.top = `${posY}px`;

            outline.animate({
                left: `${posX}px`,
                top: `${posY}px`
            }, { duration: 500, fill: "forwards" });
        });
    }

    // --- Upload & Generate ---
    function setupUpload() {
        difficultyOptions.forEach(option => {
            option.addEventListener('click', () => {
                difficultyOptions.forEach(o => o.classList.remove('active'));
                option.classList.add('active');
                state.selectedDifficulty = option.getAttribute('data-value');
            });
        });

        cardCountSlider.addEventListener('input', (e) => {
            state.selectedCardCount = parseInt(e.target.value);
            cardCountDisplay.textContent = state.selectedCardCount;
        });

        dropZone.addEventListener('click', () => fileInput.click());
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.style.borderColor = 'var(--primary)';
        });
        dropZone.addEventListener('dragleave', () => {
            dropZone.style.borderColor = 'var(--glass-border)';
        });
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.style.borderColor = 'var(--glass-border)';
            if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
        });
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length) handleFile(e.target.files[0]);
        });

        generateBtn.addEventListener('click', generateFlashcards);
    }

    function handleFile(file) {
        if (file.type !== 'application/pdf') {
            alert('Please upload a PDF file.');
            return;
        }

        state.currentFileName = file.name;
        const formData = new FormData();
        formData.append('file', file);

        dropZone.innerHTML = `
            <div class="upload-content">
                <i class="fa-solid fa-file-pdf" style="font-size: 4rem; color: var(--success)"></i>
                <h3>${file.name}</h3>
                <p>Ready to generate</p>
            </div>
        `;

        fetch('/api/upload', { method: 'POST', body: formData })
            .then(res => res.json())
            .then(data => {
                if (data.error) throw new Error(data.error);
                state.currentFile = data.filename;
                generateBtn.disabled = false;
            })
            .catch(err => alert('Upload failed: ' + err.message));
    }

    function generateFlashcards() {
        if (!state.currentFile) return;

        switchView('loading');

        fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: state.currentFile,
                difficulty: state.selectedDifficulty,
                amount: state.selectedCardCount
            })
        })
            .then(res => res.json())
            .then(data => {
                if (data.error) throw new Error(data.error);
                state.flashcards = data.flashcards;

                // Track deck creation
                fetch('/api/user/deck-created', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        deck_name: state.currentFileName,
                        cards_count: state.flashcards.length,
                        difficulty: state.selectedDifficulty
                    })
                }).then(() => refreshUserData());

                startStudySession();
            })
            .catch(err => {
                console.error(err);
                alert('Generation failed: ' + err.message);
                switchView('upload');
            });
    }

    // --- Study Session ---
    function startStudySession() {
        state.currentIndex = 0;
        totalCardsNum.textContent = state.flashcards.length;
        switchView('study');
        updateCard();
    }

    function updateCard() {
        const card = state.flashcards[state.currentIndex];

        flashcard.classList.remove('flipped');
        mcqOptions.innerHTML = '';
        mcqOptions.classList.add('hidden');

        setTimeout(() => {
            cardTypeBadge.textContent = card.type ? card.type.toUpperCase() : 'QA';
            cardQuestion.textContent = card.question;
            cardAnswer.textContent = card.answer;
            cardExplanation.textContent = card.explanation || "No explanation provided.";
            currentCardNum.textContent = state.currentIndex + 1;

            // Progress Bar
            const progress = ((state.currentIndex + 1) / state.flashcards.length) * 100;
            studyProgress.style.width = `${progress}%`;

            if (card.type === 'mcq' && card.options) {
                mcqOptions.classList.remove('hidden');
                card.options.forEach(opt => {
                    const btn = document.createElement('div');
                    btn.className = 'mcq-option';
                    btn.textContent = opt;
                    btn.onclick = (e) => checkMCQ(e, opt, card.answer);
                    mcqOptions.appendChild(btn);
                });
            }

            prevBtn.disabled = state.currentIndex === 0;

            // FIXED: Big green completion button on last card
            if (state.currentIndex === state.flashcards.length - 1) {
                nextBtn.disabled = false;
                nextBtn.innerHTML = '<i class="fa-solid fa-check"></i> Complete Deck';
                nextBtn.classList.add('completion-btn');
                nextBtn.onclick = finishDeck;
            } else {
                nextBtn.disabled = false;
                nextBtn.innerHTML = '<i class="fa-solid fa-chevron-right"></i>';
                nextBtn.classList.remove('completion-btn');
                nextBtn.onclick = nextCard;
            }

        }, 300);
    }

    function checkMCQ(e, selected, correct) {
        e.stopPropagation();
        if (selected === correct) {
            e.target.style.borderColor = 'var(--success)';
            e.target.style.background = 'rgba(34, 197, 94, 0.1)';
            confetti({ particleCount: 50, spread: 60, origin: { y: 0.7 } });
        } else {
            e.target.style.borderColor = 'var(--danger)';
            e.target.style.background = 'rgba(239, 68, 68, 0.1)';
        }
        setTimeout(() => flashcard.classList.add('flipped'), 1000);
    }

    function setupStudyControls() {
        flashcard.addEventListener('click', () => {
            flashcard.classList.toggle('flipped');
        });

        flipBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            flashcard.classList.toggle('flipped');
        });

        prevBtn.addEventListener('click', () => {
            if (state.currentIndex > 0) {
                state.currentIndex--;
                updateCard();
            }
        });
    }

    function nextCard() {
        if (state.currentIndex < state.flashcards.length - 1) {
            state.currentIndex++;
            updateCard();
        }
    }

    function finishDeck() {
        // Call completion API
        fetch('/api/user/complete-deck', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                deck_name: state.currentFileName,
                cards_count: state.flashcards.length
            })
        })
            .then(res => res.json())
            .then(result => {
                if (result.user) {
                    showCompletionModal(result);
                }
            })
            .catch(err => console.error('Completion error:', err));
    }

    function setupCompletionModal() {
        uploadNewBtn.addEventListener('click', () => {
            completionModal.classList.add('hidden');
            switchView('upload');
            resetUploadForm();
        });

        backToDashboardBtn.addEventListener('click', () => {
            completionModal.classList.add('hidden');
            switchView('dashboard');
        });
    }

    function showCompletionModal(result) {
        const { user, leveled_up, new_level } = result;
        const xpEarned = state.flashcards.length * 10;

        // Trigger confetti
        confetti({
            particleCount: 150,
            spread: 100,
            origin: { y: 0.6 }
        });

        // Update modal content
        completionXp.textContent = `+${xpEarned} XP`;
        completionTotalXp.textContent = `${user.total_xp} XP`;
        completionLevel.textContent = `Level ${user.current_level}`;
        completionCards.textContent = `${state.flashcards.length} cards`;
        completionStreak.textContent = `🔥 ${user.streak} days`;

        // Show level up badge if leveled up
        if (leveled_up) {
            newLevelSpan.textContent = new_level;
            levelUpBadge.classList.remove('hidden');
        } else {
            levelUpBadge.classList.add('hidden');
        }

        // Update user state and UI
        state.user = user;
        updateUserUI(user);

        // Show modal
        completionModal.classList.remove('hidden');
    }

    function resetUploadForm() {
        dropZone.innerHTML = `
            <div class="upload-content">
                <div class="upload-icon-wrapper">
                    <i class="fa-solid fa-cloud-arrow-up"></i>
                </div>
                <h3>Drag & Drop PDF</h3>
                <p>or click to browse</p>
            </div>
        `;
        generateBtn.disabled = true;
        state.currentFile = null;
        state.currentFileName = '';
    }

    // --- Leaderboard Logic ---
    function setupLeaderboard() {
        const refreshBtn = document.getElementById('refresh-leaderboard-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                refreshBtn.querySelector('i').classList.add('fa-spin');
                fetchLeaderboard().then(() => {
                    setTimeout(() => {
                        refreshBtn.querySelector('i').classList.remove('fa-spin');
                    }, 500);
                });
            });
        }

        // Initial fetch if on leaderboard view
        const activeView = document.querySelector('.view.active-view');
        if (activeView && activeView.id === 'view-leaderboard') {
            fetchLeaderboard();
        }

        // Add listener for view switching to leaderboard
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                const viewName = link.getAttribute('data-view');
                if (viewName === 'leaderboard') {
                    fetchLeaderboard();
                }
            });
        });
    }

    async function fetchLeaderboard() {
        try {
            const response = await fetch('/api/leaderboard');
            const data = await response.json();

            if (data.leaderboard) {
                renderLeaderboardList(data.leaderboard);

                // Update current user rank in state if possible
                if (state.user) {
                    const userEntry = data.leaderboard.find(u => u.id === state.user.id);
                    if (userEntry) {
                        state.user.rank = userEntry.rank;
                    }
                }
            }
        } catch (error) {
            console.error('Error fetching leaderboard:', error);
        }
    }

    function renderLeaderboardList(users) {
        const listContainer = document.getElementById('leaderboard-list');
        if (!listContainer) return;

        listContainer.innerHTML = '';

        if (users.length === 0) {
            listContainer.innerHTML = `
                <div class="leaderboard-empty">
                    <i class="fa-solid fa-users-slash"></i>
                    <p>No more learners yet. Be the first!</p>
                </div>
            `;
            return;
        }

        users.forEach(user => {
            const isCurrentUser = state.user && user.id === state.user.id;
            const row = document.createElement('div');
            row.className = `table-row ${isCurrentUser ? 'current-user' : ''}`;
            row.setAttribute('data-user-id', user.id);

            // Rank styling
            let rankClass = '';
            if (user.rank === 1) rankClass = 'rank-1 top-3-rank';
            else if (user.rank === 2) rankClass = 'rank-2 top-3-rank';
            else if (user.rank === 3) rankClass = 'rank-3 top-3-rank';

            row.innerHTML = `
                <div class="rank-cell">
                    <div class="${rankClass}">${user.rank}</div>
                </div>
                <div class="user-cell">
                    <div class="user-avatar-small">
                        <i class="fa-solid fa-user"></i>
                    </div>
                    ${user.username}
                    ${isCurrentUser ? '<span class="you-badge">YOU</span>' : ''}
                </div>
                <div class="level-cell">
                    <span class="level-badge">Lvl ${user.current_level}</span>
                </div>
                <div class="xp-cell">
                    ${user.total_xp} XP
                </div>
            `;

            listContainer.appendChild(row);
        });
    }
});
