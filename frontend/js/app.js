const { createApp } = Vue;

createApp({
    data() {
        return {
            readingWord: null,        // 阅读模式当前 word
            spellingWord: null,       // 拼写模式 current word
            randomWord: null,         // 随机模式 current word
            firstId: null,
            lastId: null,
            total: 0,
            loading: false,
            error: null,
            currentMode: 'reading',
            sidebarsHidden: false,
            spellInput: '',
            spellResult: null,
            spellingHintPositions: [],
            spellingAnswer: [],
            spellingActiveSlot: -1,
            spellShake: false,
            spellingWordResults: {},  // { wordId: { result: 'correct'|'revealed', answer: [], hints: [] } }
            seenWordIds: [],
            toastVisible: false,
            toastMessage: '',
            toastTimer: null,
            readingTranslationVisible: false,
            randomTranslationVisible: false,
            // AI 助手相关状态
            aiMessages: [],         // 对话消息列表 [{role: 'user'|'assistant', content: '...'}]
            aiInput: '',            // 用户输入框内容
            aiLoading: false,       // AI 是否正在响应
            // 登录相关
            showLoginModal: false,    // 是否显示登录弹窗
            showRegisterModal: false, // 是否显示注册弹窗
            showProfileModal: false,  // 是否显示个人信息弹窗
            currentUser: null,        // 当前登录用户
            loginEmail: '',           // 登录邮箱（替代原用户名）
            loginPassword: '',        // 登录密码
            loginLoading: false,      // 登录中
            loginError: '',           // 登录错误信息
            // 注册相关
            registerNickname: '',     // 注册昵称
            registerEmail: '',        // 注册邮箱
            registerPassword: '',     // 注册密码
            registerLoading: false,   // 注册中
            registerError: '',        // 注册错误信息
            registerSuccess: '',      // 注册成功提示
            // 个人信息表单（仅昵称和密码可修改）
            profileForm: { nickname: '', password: '' },
            profileSaving: false,
            profileSaveMsg: { text: '', type: '' },
            // 收藏功能相关状态
            readingWordIsFavorite: false,     // 阅读模式当前单词是否已收藏
            spellingWordIsFavorite: false,    // 拼写模式当前单词是否已收藏
            randomWordIsFavorite: false,      // 随机模式当前单词是否已收藏
            showFavoritesModal: false,        // 是否显示收藏列表弹窗
            favoritesList: [],                // 收藏列表
            favoritesLoading: false,          // 收藏列表加载中
            // 错题本功能相关状态
            showMistakesModal: false,         // 是否显示错题本弹窗
            mistakesList: [],                 // 错题列表
            mistakesLoading: false,           // 错题列表加载中
            // 例句滑动相关
            exampleDragStartX: 0,
            exampleStartScrollLeft: 0,
            isDragging: false
        };
    },
    computed: {
        // 阅读模式
        readingIsFirst() { return this.readingWord && this.readingWord.id === this.firstId; },
        readingIsLast() { return this.readingWord && this.readingWord.id === this.lastId; },
        // 拼写模式
        spellingIsFirst() { return this.spellingWord && this.spellingWord.id === this.firstId; },
        spellingIsLast() { return this.spellingWord && this.spellingWord.id === this.lastId; },
        hintCount() {
            if (!this.spellingWord) return 0;
            return Math.floor(this.spellingWord.word.length / 2.5);
        },
        letterSlots() {
            if (!this.spellingWord) return [];
            const word = this.spellingWord.word;
            return word.split('').map((letter, i) => {
                const isHint = this.spellingHintPositions.includes(i);
                let display = '';
                if (isHint) display = letter;
                else if (this.spellingAnswer[i]) display = this.spellingAnswer[i];
                return { letter, isHint, display };
            });
        },
    },
    methods: {
        // ===== 登录相关 =====
        toggleLoginModal() {
            this.showLoginModal = !this.showLoginModal;
            this.loginError = '';
        },
        openProfileModal() {
            if (this.currentUser) {
                // 已登录：打开个人信息表单，回填昵称（邮箱仅展示不可修改）
                this.profileForm = {
                    nickname: this.currentUser.nickname || '',
                    password: ''
                };
                this.profileSaveMsg = { text: '', type: '' };
                this.showProfileModal = true;
            } else {
                // 未登录：显示登录弹窗
                this.showLoginModal = true;
                this.loginError = '';
            }
        },
        openRegisterModal() {
            // 关闭登录弹窗，打开注册弹窗，重置注册表单状态
            this.showLoginModal = false;
            this.showRegisterModal = true;
            this.registerNickname = '';
            this.registerEmail = '';
            this.registerPassword = '';
            this.registerError = '';
            this.registerSuccess = '';
        },
        backToLogin() {
            // 关闭注册弹窗，返回登录弹窗
            this.showRegisterModal = false;
            this.showLoginModal = true;
            this.loginError = '';
        },
        async handleRegister() {
            // 1. 校验昵称不为空
            if (!this.registerNickname.trim()) {
                this.registerError = '请输入昵称';
                return;
            }
            // 2. 校验邮箱格式
            if (!this.registerEmail.includes('@') || !this.registerEmail.includes('.')) {
                this.registerError = '请输入正确的邮箱地址';
                return;
            }
            // 3. 校验密码长度
            if (this.registerPassword.length < 6) {
                this.registerError = '密码长度不能少于6位';
                return;
            }
            try {
                this.registerLoading = true;
                this.registerError = '';
                this.registerSuccess = '';
                // 4. 调用注册接口
                const res = await axios.post('http://localhost:3000/api/auth/register', {
                    nickname: this.registerNickname.trim(),
                    email: this.registerEmail.trim(),
                    password: this.registerPassword
                });
                // 5. 注册成功，提示后跳转登录
                this.registerSuccess = '注册成功！即将跳转到登录...';
                setTimeout(() => {
                    this.showRegisterModal = false;
                    this.showLoginModal = true;
                    this.loginEmail = this.registerEmail.trim(); // 自动填入邮箱
                    this.loginPassword = '';
                    this.registerSuccess = '';
                }, 1500);
            } catch (err) {
                this.registerError = err.response?.data?.detail || '注册失败，请检查网络';
            } finally {
                this.registerLoading = false;
            }
        },
        async handleLogin() {
            if (!this.loginEmail || !this.loginPassword) return;
            try {
                this.loginLoading = true;
                this.loginError = '';
                // 使用邮箱 + 密码调用登录接口
                const res = await axios.post('http://localhost:3000/api/auth/login', {
                    email: this.loginEmail,
                    password: this.loginPassword
                });
                this.currentUser = res.data.user;
                localStorage.setItem('currentUser', JSON.stringify(this.currentUser));
                this.showLoginModal = false;
                this.loginEmail = '';
                this.loginPassword = '';
                this.showToast('登录成功，欢迎 ' + (this.currentUser.nickname || this.currentUser.username));
                // 登录成功后刷新页面
                setTimeout(() => {
                    location.reload();
                }, 1500);
            } catch (err) {
                this.loginError = err.response?.data?.detail || '登录失败，请检查邮箱和密码';
            } finally {
                this.loginLoading = false;
            }
        },
        handleLogout() {
            this.currentUser = null;
            this.showProfileModal = false;
            localStorage.removeItem('currentUser');
            this.showToast('已退出登录');
            // 退出登录后刷新页面
            setTimeout(() => {
                location.reload();
            }, 1000);
        },
        async saveProfile() {
            if (!this.currentUser || this.profileSaving) return;
            try {
                this.profileSaving = true;
                this.profileSaveMsg = { text: '', type: '' };
                const data = {};
                // 仅判断昵称是否修改
                if (this.profileForm.nickname !== (this.currentUser.nickname || '')) data.nickname = this.profileForm.nickname;
                // 判断密码是否填写（留空则不修改）
                if (this.profileForm.password.trim()) data.password = this.profileForm.password;
                if (Object.keys(data).length === 0) {
                    this.profileSaveMsg = { text: '没有修改任何内容', type: 'error' };
                    return;
                }
                const res = await axios.put(`http://localhost:3000/api/auth/profile/${this.currentUser.id}`, data);
                // 更新本地存储
                this.currentUser = res.data;
                localStorage.setItem('currentUser', JSON.stringify(this.currentUser));
                this.profileSaveMsg = { text: '保存成功！', type: 'success' };
                this.profileForm.password = '';
            } catch (err) {
                this.profileSaveMsg = { text: err.response?.data?.detail || '保存失败', type: 'error' };
            } finally {
                this.profileSaving = false;
            }
        },
        checkLoginStatus() {
            const saved = localStorage.getItem('currentUser');
            if (saved) {
                try { this.currentUser = JSON.parse(saved); } catch (e) { }
            }
        },

        // 初始化：获取单词总数和第一个单词（阅读模式）
        async fetchCurrentWord() {
            try {
                this.loading = true;
                this.error = null;
                const [boundsRes, countRes] = await Promise.all([
                    axios.get('http://localhost:3000/api/words/first-last'),
                    axios.get('http://localhost:3000/api/words/count')
                ]);
                this.firstId = boundsRes.data.first_id;
                this.lastId = boundsRes.data.last_id;
                this.total = countRes.data.total;
                const wordRes = await axios.get('http://localhost:3000/api/words/current');
                this.readingWord = wordRes.data;
                this.readingTranslationVisible = false;
            } catch (err) {
                console.error('获取单词失败:', err);
                this.error = '获取单词失败，请确保后端服务正在运行';
            } finally { this.loading = false; }
        },

        // ===== 阅读模式 =====
        async nextWord() {
            if (this.readingIsLast || this.loading) return;
            try {
                this.loading = true; this.error = null;
                const res = await axios.get(`http://localhost:3000/api/words/next/${this.readingWord.id}`);
                if (res.data) { this.readingWord = res.data; this.readingTranslationVisible = false; }
            } catch (err) { console.error(err); this.error = '获取下一个单词失败'; }
            finally { this.loading = false; }
        },
        async prevWord() {
            if (this.readingIsFirst || this.loading) return;
            try {
                this.loading = true; this.error = null;
                const res = await axios.get(`http://localhost:3000/api/words/prev/${this.readingWord.id}`);
                if (res.data) { this.readingWord = res.data; this.readingTranslationVisible = false; }
            } catch (err) { console.error(err); this.error = '获取上一个单词失败'; }
            finally { this.loading = false; }
        },

        // ===== 拼写模式 =====
        generateHints() {
            const word = this.spellingWord.word;
            const len = word.length;
            const count = Math.floor(len / 2.5);
            const positions = [];
            const indices = Array.from({ length: len }, (_, i) => i);
            for (let i = 0; i < count; i++) {
                const randIdx = Math.floor(Math.random() * indices.length);
                positions.push(indices[randIdx]);
                indices.splice(randIdx, 1);
            }
            this.spellingHintPositions = positions.sort((a, b) => a - b);
            this.spellingAnswer = new Array(len).fill('');
            this.spellingActiveSlot = -1;
            this.$nextTick(() => this.focusFirstEmptySlot());
        },
        focusInput() {
            this.$nextTick(() => {
                if (this.$refs.hiddenInput) {
                    this.$refs.hiddenInput.value = '';
                    this.$refs.hiddenInput.focus();
                }
            });
        },
        focusFirstEmptySlot() {
            const firstEmpty = this.letterSlots.findIndex(s => !s.isHint);
            this.spellingActiveSlot = firstEmpty !== -1 ? firstEmpty : 0;
            this.focusInput();
        },
        onSlotClick(index) {
            if (this.spellResult) return;
            const slot = this.letterSlots[index];
            if (slot.isHint) {
                const next = this.letterSlots.findIndex((s, i) => i > index && !s.isHint);
                if (next !== -1) {
                    this.spellingActiveSlot = next;
                }
                return;
            }
            this.spellingActiveSlot = index;
            this.focusInput();
        },
        onHiddenInput(e) {
            const val = e.target.value;
            if (!val || this.spellingActiveSlot < 0) {
                e.target.value = '';
                return;
            }
            const lastChar = val[val.length - 1];
            if (lastChar === ' ') { e.target.value = ''; return; }
            // 填入字母
            if (this.spellingActiveSlot >= 0 && !this.letterSlots[this.spellingActiveSlot].isHint) {
                this.spellingAnswer[this.spellingActiveSlot] = lastChar;
                // 自动跳到下一个非提示空格
                let next = this.spellingActiveSlot + 1;
                while (next < this.letterSlots.length && this.letterSlots[next].isHint) next++;
                if (next < this.letterSlots.length) {
                    this.spellingActiveSlot = next;
                }
            }
            e.target.value = '';
            this.$nextTick(() => {
                if (this.$refs.hiddenInput) this.$refs.hiddenInput.focus();
            });
            // 检查是否所有非提示格都已填满，自动判断
            const allFilled = this.letterSlots.every((s, i) => s.isHint || this.spellingAnswer[i]);
            if (allFilled) {
                setTimeout(() => this.checkSpelling(), 300);
            }
        },
        onHiddenKeydown(e) {
            if (e.key === 'Backspace') {
                e.preventDefault();
                if (this.spellingAnswer[this.spellingActiveSlot]) {
                    this.spellingAnswer[this.spellingActiveSlot] = '';
                } else {
                    let prev = this.spellingActiveSlot - 1;
                    while (prev >= 0 && this.letterSlots[prev].isHint) prev--;
                    if (prev >= 0) {
                        this.spellingAnswer[prev] = '';
                        this.spellingActiveSlot = prev;
                    }
                }
                this.$nextTick(() => {
                    if (this.$refs.hiddenInput) {
                        this.$refs.hiddenInput.value = '';
                        this.$refs.hiddenInput.focus();
                    }
                });
            }
        },
        saveCurrentWordState(includeRevealed = false) {
            if (!this.spellingWord) return;
            const id = this.spellingWord.id;
            if (this.spellResult === 'correct') {
                // 绿色通过：始终保存
                this.spellingWordResults[id] = {
                    result: 'correct',
                    answer: [...this.spellingAnswer],
                    hints: [...this.spellingHintPositions]
                };
            } else if (includeRevealed && this.spellResult === 'revealed') {
                // 红色"我不会"：仅模式切换时保存，模式内导航不保存
                this.spellingWordResults[id] = {
                    result: 'revealed',
                    answer: [...this.spellingAnswer],
                    hints: [...this.spellingHintPositions]
                };
            }
            // 未答对（正在输入中）：不保存
        },
        restoreWordState() {
            const id = this.spellingWord.id;
            const saved = this.spellingWordResults[id];
            if (saved && (saved.result === 'correct' || saved.result === 'revealed')) {
                // 有保存的状态（绿色通过 或 模式切换保留的红色"我不会"）：恢复
                this.spellingHintPositions = [...saved.hints];
                this.spellingAnswer = [...saved.answer];
                this.spellResult = saved.result;
                this.spellingActiveSlot = -1;
            } else {
                // 无记录：重新生成提示
                this.generateHints();
            }
        },
        // 模式内导航专用：到达目标单词后调用
        // 清除 revealed 保存记录（来自模式切换），只恢复 correct
        restoreForNavigation() {
            const id = this.spellingWord.id;
            const saved = this.spellingWordResults[id];
            if (saved && saved.result === 'revealed') {
                // 之前通过模式切换保存的红色状态：清除，需要重新拼写
                delete this.spellingWordResults[id];
                this.generateHints();
            } else {
                // correct 或无记录：正常恢复
                this.restoreWordState();
            }
        },
        async nextWordSpell() {
            if (this.spellingIsLast || this.loading) return;
            this.saveCurrentWordState();
            try {
                this.loading = true; this.error = null;
                const res = await axios.get(`http://localhost:3000/api/words/next/${this.spellingWord.id}`);
                if (res.data) { this.spellingWord = res.data; this.resetSpell(); this.restoreForNavigation(); }
            } catch (err) { console.error(err); this.error = '获取下一个单词失败'; }
            finally { this.loading = false; }
        },
        async prevWordSpell() {
            if (this.spellingIsFirst || this.loading) return;
            this.saveCurrentWordState();
            try {
                this.loading = true; this.error = null;
                const res = await axios.get(`http://localhost:3000/api/words/prev/${this.spellingWord.id}`);
                if (res.data) { this.spellingWord = res.data; this.resetSpell(); this.restoreForNavigation(); }
            } catch (err) { console.error(err); this.error = '获取上一个单词失败'; }
            finally { this.loading = false; }
        },
        checkSpelling() {
            if (!this.spellingWord) return;
            const word = this.spellingWord.word;
            const answer = word.split('').map((letter, i) => {
                if (this.spellingHintPositions.includes(i)) return letter;
                return this.spellingAnswer[i] || '';
            });
            const isCorrect = answer.join('').toLowerCase() === word.toLowerCase();
            if (isCorrect) {
                this.spellResult = 'correct';
                // 拼写正确，减少错误次数
                this.reduceMistake(this.spellingWord.id);
            } else {
                // 错误：闪红+抖动动画，然后重置让用户重试
                this.spellShake = true;
                // 添加到错题本
                this.addMistake(this.spellingWord.id);
                setTimeout(() => {
                    this.spellShake = false;
                    this.spellingAnswer = new Array(word.length).fill('');
                    this.spellingActiveSlot = -1;
                    this.focusFirstEmptySlot();
                }, 600);
            }
        },
        showAnswer() {
            if (!this.spellingWord) return;
            const word = this.spellingWord.word;
            this.spellingAnswer = word.split('').map((letter, i) => {
                if (this.spellingHintPositions.includes(i)) return letter;
                return letter;
            });
            this.spellResult = 'revealed';
            // 点击"我不会"，添加到错题本
            this.addMistake(this.spellingWord.id);
        },
        goNextAfterCorrect() {
            if (this.spellResult !== 'correct') return;
            if (!this.spellingIsLast) this.nextWordSpell();
        },
        resetSpell() {
            this.spellInput = '';
            this.spellResult = null;
            this.spellingActiveSlot = -1;
            this.spellingAnswer = [];
            this.spellingHintPositions = [];
        },

        // ===== 随机模式 =====
        switchToRandom() {
            this.currentMode = 'random';
            // 如果已有进度则保留，否则初始化
            if (!this.randomWord) {
                this.fetchNewRandomWord();
            }
        },
        async handleReset() {
            // 重置随机模式，清空已刷单词列表
            if (this.loading) return;
            try {
                this.loading = true;
                this.error = null;
                this.seenWordIds = [];
                this.randomWord = null;
                await this.fetchNewRandomWord();
                this.showToast('已重置学习进度');
            } catch (err) {
                console.error('重置失败:', err);
                this.error = '重置失败';
            } finally {
                this.loading = false;
            }
        },
        async fetchNewRandomWord() {
            try {
                this.loading = true; this.error = null;
                const excludeStr = this.seenWordIds.join(',');
                const res = await axios.get(`http://localhost:3000/api/words/random?exclude=${excludeStr}`);
                if (res.data) {
                    this.randomWord = res.data;
                    this.randomTranslationVisible = false;
                    if (!this.seenWordIds.includes(res.data.id)) {
                        this.seenWordIds.push(res.data.id);
                    }
                }
            } catch (err) {
                console.error(err);
                if (err.response && err.response.status === 404) {
                    this.error = '所有单词都已刷完啦！可以点左边的按钮复习';
                } else { this.error = '获取随机单词失败'; }
            } finally { this.loading = false; }
        },
        async reviewSeenWord() {
            if (this.seenWordIds.length === 0 || this.loading) return;
            try {
                this.loading = true; this.error = null;
                const seenStr = this.seenWordIds.join(',');
                const res = await axios.get(`http://localhost:3000/api/words/random/seen?seen=${seenStr}`);
                if (res.data) { this.randomWord = res.data; this.randomTranslationVisible = false; }
            } catch (err) { console.error(err); this.error = '获取已刷单词失败'; }
            finally { this.loading = false; }
        },
        async handleResetIfComplete() {
            // 根据当前状态决定调用重置还是获取新单词
            if (this.seenWordIds.length >= this.total) {
                await this.handleReset();
            } else {
                await this.fetchNewRandomWord();
            }
        },

        // 拼写模式初始化：进入拼写模式时如果没有单词则获取第一个
        initSpelling() {
            if (!this.spellingWord && this.total > 0) {
                axios.get('http://localhost:3000/api/words/current').then(res => {
                    this.spellingWord = res.data;
                    this.$nextTick(() => this.restoreWordState());
                });
            } else if (this.spellingWord) {
                // 切回拼写模式：优先恢复绿色通过状态，否则重新生成提示
                this.resetSpell();
                this.restoreWordState();
            }
        },

        // ===== AI 沟通模式 =====
        switchToAi() {
            // 切换到 AI 沟通模式
            this.currentMode = 'ai';
            // 切换后自动聚焦输入框
            this.$nextTick(() => {
                if (this.$refs.aiChatInput) this.$refs.aiChatInput.focus();
            });
        },
        // 快捷按钮：根据类型发送预设问题
        aiQuickAsk(type) {
            const prompts = {
                'explain': '请教我一个英语单词，我会输入单词名',
                'examples': '请给我一些常用的英语日常对话例句',
                'grammar': '请给我讲解一个常见的英语语法知识点',
                'translate': '请帮我翻译一句中文成英文'
            };
            // 将预设提示填入输入框，让用户可以修改后发送
            this.aiInput = prompts[type] || '';
            this.$nextTick(() => {
                if (this.$refs.aiChatInput) this.$refs.aiChatInput.focus();
            });
        },
        // 发送自由问答
        async sendAiChat() {
            // 获取并校验输入
            const question = this.aiInput.trim();
            if (!question || this.aiLoading) return;
            // 添加用户消息到列表
            this.aiMessages.push({ role: 'user', content: question });
            this.aiInput = '';  // 清空输入框
            this.scrollAiToBottom();
            // 调用后端 AI 接口
            await this.callAiApi('http://localhost:3000/api/ai/chat', {
                word: '',
                meaning: '',
                question: question
            });
        },
        // 通用 AI 接口调用
        async callAiApi(url, data) {
            try {
                this.aiLoading = true;
                // 先添加一个 loading 占位消息
                this.aiMessages.push({ role: 'assistant', content: '思考中...' });
                this.scrollAiToBottom();
                // 发送 POST 请求到后端
                const res = await axios.post(url, data);
                // 替换最后一条消息为 AI 的真实回复
                this.aiMessages[this.aiMessages.length - 1] = {
                    role: 'assistant',
                    content: res.data.answer
                };
            } catch (err) {
                // 请求失败时显示错误提示
                this.aiMessages[this.aiMessages.length - 1] = {
                    role: 'assistant',
                    content: '❌ 请求失败，请检查后端服务是否启动，以及 AI API Key 是否配置正确。'
                };
                console.error('AI 请求失败:', err);
            } finally {
                this.aiLoading = false;
                this.scrollAiToBottom();
            }
        },
        // 滚动 AI 消息列表到底部
        scrollAiToBottom() {
            this.$nextTick(() => {
                const el = this.$refs.aiChatMessages;
                if (el) el.scrollTop = el.scrollHeight;
            });
        },

        // 隐藏侧边栏 + 显示 Toast
        toggleSidebars() {
            this.sidebarsHidden = true;
            this.showToast('隐藏侧边栏成功，鼠标触碰任意侧边栏弹出');
        },

        // 鼠标触碰边界时显示侧边栏
        showSidebars() {
            this.sidebarsHidden = false;
        },

        // Toast 提示（非弹窗，2秒后淡出）
        showToast(message) {
            if (this.toastTimer) clearTimeout(this.toastTimer);
            this.toastMessage = message;
            this.toastVisible = true;
            this.toastTimer = setTimeout(() => {
                this.toastVisible = false;
            }, 2000);
        },

        // 切换到拼写模式时初始化
        switchToSpelling() {
            if (this.currentMode === 'spelling') return; // 已在拼写模式，不重复初始化
            this.currentMode = 'spelling';
            this.initSpelling();
        },

        // ===== 收藏功能 =====
        async checkFavoriteStatus(wordId) {
            // 检查单词是否已收藏
            if (!this.currentUser || !wordId) {
                return false;
            }
            try {
                const res = await axios.post('http://localhost:3000/api/favorites/check', {
                    user_id: this.currentUser.id,
                    word_id: wordId
                });
                return res.data.is_favorited;
            } catch (err) {
                console.error('检查收藏状态失败:', err);
                return false;
            }
        },
        async toggleFavorite() {
            // 切换收藏状态
            if (!this.currentUser) {
                this.showToast('请先登录');
                return;
            }

            // 根据当前模式获取当前单词
            let currentWord = null;
            let isFavoriteState = null;

            if (this.currentMode === 'reading' && this.readingWord) {
                currentWord = this.readingWord;
                isFavoriteState = 'readingWordIsFavorite';
            } else if (this.currentMode === 'spelling' && this.spellingWord) {
                currentWord = this.spellingWord;
                isFavoriteState = 'spellingWordIsFavorite';
            } else if (this.currentMode === 'random' && this.randomWord) {
                currentWord = this.randomWord;
                isFavoriteState = 'randomWordIsFavorite';
            } else {
                return;
            }

            try {
                const res = await axios.post('http://localhost:3000/api/favorites/toggle', {
                    user_id: this.currentUser.id,
                    word_id: currentWord.id
                });

                // 更新收藏状态
                this[isFavoriteState] = res.data.is_favorited;
                this.showToast(res.data.message);
            } catch (err) {
                console.error('切换收藏失败:', err);
                this.showToast('操作失败，请重试');
            }
        },
        openFavoritesModal() {
            // 打开收藏列表弹窗
            if (!this.currentUser) {
                this.showToast('请先登录');
                this.showLoginModal = true;
                return;
            }
            this.showFavoritesModal = true;
            this.fetchFavoritesList();
        },
        async fetchFavoritesList() {
            // 获取收藏列表
            if (!this.currentUser) return;

            try {
                this.favoritesLoading = true;
                const res = await axios.get(`http://localhost:3000/api/favorites/list/${this.currentUser.id}`);
                this.favoritesList = res.data.favorites;
            } catch (err) {
                console.error('获取收藏列表失败:', err);
                this.favoritesList = [];
                this.showToast('获取收藏列表失败');
            } finally {
                this.favoritesLoading = false;
            }
        },
        async deleteFavorite(wordId) {
            // 从收藏列表中删除单词（通过toggle接口实现）
            if (!this.currentUser) return;

            try {
                const res = await axios.post('http://localhost:3000/api/favorites/toggle', {
                    user_id: this.currentUser.id,
                    word_id: wordId
                });

                // 从列表中移除该项
                this.favoritesList = this.favoritesList.filter(item => item.id !== wordId);
                this.showToast(res.data.message);

                // 实时更新当前单词的收藏状态
                if (this.currentMode === 'reading' && this.readingWord && this.readingWord.id === wordId) {
                    this.readingWordIsFavorite = false;
                } else if (this.currentMode === 'spelling' && this.spellingWord && this.spellingWord.id === wordId) {
                    this.spellingWordIsFavorite = false;
                } else if (this.currentMode === 'random' && this.randomWord && this.randomWord.id === wordId) {
                    this.randomWordIsFavorite = false;
                }
            } catch (err) {
                console.error('取消收藏失败:', err);
                this.showToast('操作失败，请重试');
            }
        },

        // ===== 错题本功能 =====
        async addMistake(wordId) {
            // 添加错题或增加错误次数
            if (!this.currentUser || !wordId) return;

            try {
                const res = await axios.post('http://localhost:3000/api/mistakes/add', {
                    user_id: this.currentUser.id,
                    word_id: wordId
                });
                return res.data;
            } catch (err) {
                console.error('添加错题失败:', err);
                return null;
            }
        },
        async reduceMistake(wordId) {
            // 减少错误次数
            if (!this.currentUser || !wordId) return;

            try {
                const res = await axios.post('http://localhost:3000/api/mistakes/reduce', {
                    user_id: this.currentUser.id,
                    word_id: wordId
                });
                return res.data;
            } catch (err) {
                console.error('减少错误次数失败:', err);
                return null;
            }
        },
        openMistakesModal() {
            // 打开错题本弹窗
            if (!this.currentUser) {
                this.showToast('请先登录');
                this.showLoginModal = true;
                return;
            }
            this.showMistakesModal = true;
            this.fetchMistakesList();
        },
        async fetchMistakesList() {
            // 获取错题列表
            if (!this.currentUser) return;

            try {
                this.mistakesLoading = true;
                const res = await axios.get(`http://localhost:3000/api/mistakes/list/${this.currentUser.id}`);
                this.mistakesList = res.data.mistakes;
            } catch (err) {
                console.error('获取错题列表失败:', err);
                this.mistakesList = [];
                this.showToast('获取错题列表失败');
            } finally {
                this.mistakesLoading = false;
            }
        },
        async deleteMistake(userId, wordId) {
            // 从错题本中删除单词
            if (!this.currentUser) return;

            try {
                const res = await axios.post('http://localhost:3000/api/mistakes/remove', {
                    user_id: this.currentUser.id,
                    word_id: wordId
                });

                // 从列表中移除该项
                this.mistakesList = this.mistakesList.filter(item => item.id !== wordId);
                this.showToast(res.data.message);
            } catch (err) {
                console.error('删除错题失败:', err);
                this.showToast('操作失败，请重试');
            }
        },

        // ===== 例句滑动功能 =====
        onExampleMouseDown(e) {
            const target = e.currentTarget;
            const scrollWidth = target.scrollWidth;
            const clientWidth = target.clientWidth;

            if (scrollWidth <= clientWidth) return;

            this.isDragging = true;
            this.exampleDragStartX = e.clientX;
            this.exampleStartScrollLeft = target.scrollLeft;

            document.addEventListener('mousemove', this.onExampleMouseMove);
            document.addEventListener('mouseup', this.onExampleMouseUp);
        },
        onExampleMouseMove(e) {
            if (!this.isDragging) return;

            const exampleText = document.querySelector('.example-text');
            if (!exampleText) return;

            const deltaX = this.exampleDragStartX - e.clientX;
            let newScrollLeft = this.exampleStartScrollLeft + deltaX;

            const maxScrollLeft = exampleText.scrollWidth - exampleText.clientWidth;
            newScrollLeft = Math.max(0, Math.min(maxScrollLeft, newScrollLeft));

            exampleText.scrollLeft = newScrollLeft;
        },
        onExampleMouseUp() {
            this.isDragging = false;
            document.removeEventListener('mousemove', this.onExampleMouseMove);
            document.removeEventListener('mouseup', this.onExampleMouseUp);
        },
        resetExampleScroll() {
            const exampleTexts = document.querySelectorAll('.example-text');
            exampleTexts.forEach(el => {
                el.scrollLeft = 0;
            });
        }
    },
    mounted() {
        this.fetchCurrentWord();
        this.checkLoginStatus();
    },
    watch: {
        // 监听阅读模式单词变化
        readingWord: {
            handler(newWord) {
                if (newWord && this.currentUser) {
                    this.checkFavoriteStatus(newWord.id).then(isFav => {
                        this.readingWordIsFavorite = isFav;
                    });
                } else {
                    this.readingWordIsFavorite = false;
                }
            },
            immediate: true
        },
        // 监听拼写模式单词变化
        spellingWord: {
            handler(newWord) {
                if (newWord && this.currentUser) {
                    this.checkFavoriteStatus(newWord.id).then(isFav => {
                        this.spellingWordIsFavorite = isFav;
                    });
                } else {
                    this.spellingWordIsFavorite = false;
                }
            },
            immediate: true
        },
        // 监听随机模式单词变化
        randomWord: {
            handler(newWord) {
                if (newWord && this.currentUser) {
                    this.checkFavoriteStatus(newWord.id).then(isFav => {
                        this.randomWordIsFavorite = isFav;
                    });
                } else {
                    this.randomWordIsFavorite = false;
                }
            },
            immediate: true
        },
        // 监听用户登录状态变化
        currentUser: {
            handler(newUser) {
                if (newUser) {
                    // 用户登录后，检查当前单词的收藏状态
                    if (this.readingWord) {
                        this.checkFavoriteStatus(this.readingWord.id).then(isFav => {
                            this.readingWordIsFavorite = isFav;
                        });
                    }
                    if (this.spellingWord) {
                        this.checkFavoriteStatus(this.spellingWord.id).then(isFav => {
                            this.spellingWordIsFavorite = isFav;
                        });
                    }
                    if (this.randomWord) {
                        this.checkFavoriteStatus(this.randomWord.id).then(isFav => {
                            this.randomWordIsFavorite = isFav;
                        });
                    }
                } else {
                    // 用户退出登录后，重置收藏状态
                    this.readingWordIsFavorite = false;
                    this.spellingWordIsFavorite = false;
                    this.randomWordIsFavorite = false;
                    this.favoritesList = [];
                }
            },
            immediate: true
        },
        currentMode(newVal, oldVal) {
            // 离开拼写模式时自动保存当前单词状态（包括红色"我不会"）
            if (oldVal === 'spelling' && newVal !== 'spelling') {
                this.saveCurrentWordState(true);
            }
            // 切换模式时重置翻译状态
            if (oldVal !== newVal) {
                this.readingTranslationVisible = false;
                this.randomTranslationVisible = false;
            }
            // 切换模式时，刷新当前单词的收藏状态
            if (this.currentUser) {
                if (this.readingWord) {
                    this.checkFavoriteStatus(this.readingWord.id).then(isFav => {
                        this.readingWordIsFavorite = isFav;
                    });
                }
                if (this.spellingWord) {
                    this.checkFavoriteStatus(this.spellingWord.id).then(isFav => {
                        this.spellingWordIsFavorite = isFav;
                    });
                }
                if (this.randomWord) {
                    this.checkFavoriteStatus(this.randomWord.id).then(isFav => {
                        this.randomWordIsFavorite = isFav;
                    });
                }
            }
        }
    }
}).mount('#app');