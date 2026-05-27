// ========================================
// CHATBOT OPEN / CLOSE
// ========================================

function toggleChat() {

    const chatbot = document.getElementById('chatbot');

    // CHECK DISPLAY

    if (
        chatbot.style.display === 'flex'
    ) {

        chatbot.style.display = 'none';

    } else {

        chatbot.style.display = 'flex';
    }
}

// ========================================
// FIND JOBS FUNCTION
// ========================================

async function findJobs() {

    // GET VALUES

    const role =
    document.getElementById('role').value;

    const skills =
    document.getElementById('skills').value;

    // VALIDATION

    if (
        role.trim() === '' ||
        skills.trim() === ''
    ) {

        alert(
            'Please enter role and skills'
        );

        return;
    }

    // SHOW LOADING

    document.getElementById(
        'results'
    ).innerHTML = `

        <div class="loading">

            Finding best jobs for you...

        </div>

    `;

    try {

        // FETCH API

        const response = await fetch(
            '/recommend',
            {

                method: 'POST',

                headers: {

                    'Content-Type':
                    'application/json'
                },

                body: JSON.stringify({

                    role: role,
                    skills: skills
                })
            }
        );

        // JSON DATA

        const data =
        await response.json();

        let html = '';

        // NO DATA

        if (data.length === 0) {

            html = `

                <div class="no-results">

                    No matching jobs found.

                </div>

            `;

        } else {

            // LOOP RESULTS

            data.forEach(job => {

                html += `

                <div class="job-card">

                    <div class="job-top">

                        <h3>
                            ${job.company}
                        </h3>

                        <span class="match-badge">

                            ${job.match}% Match

                        </span>

                    </div>

                    <p>

                        <strong>
                            Role:
                        </strong>

                        ${job.role}

                    </p>

                    <p>

                        <strong>
                            Skills:
                        </strong>

                        ${job.skills}

                    </p>

                    <button class="apply-btn">

                        Apply Now

                    </button>

                </div>

                `;
            });
        }

        // DISPLAY RESULTS

        document.getElementById(
            'results'
        ).innerHTML = html;

    } catch (error) {

        console.log(error);

        document.getElementById(
            'results'
        ).innerHTML = `

            <div class="error">

                Something went wrong.

            </div>

        `;
    }
}

// ========================================
// SEND CHAT MESSAGE
// ========================================

async function sendMessage() {

    // GET INPUT

    const input =
    document.getElementById(
        'chatInput'
    );

    const message =
    input.value.trim();

    // EMPTY CHECK

    if (message === '') return;

    const chatBody =
    document.getElementById(
        'chatBody'
    );

    // USER MESSAGE

    chatBody.innerHTML += `

        <div class="user-message">

            ${message}

        </div>

    `;

    // CLEAR INPUT

    input.value = '';

    // AUTO SCROLL

    chatBody.scrollTop =
    chatBody.scrollHeight;

    try {

        // SEND TO BACKEND

        const response = await fetch(
            '/chat',
            {

                method: 'POST',

                headers: {

                    'Content-Type':
                    'application/json'
                },

                body: JSON.stringify({

                    message: message
                })
            }
        );

        // RECEIVE DATA

        const data =
        await response.json();

        // BOT MESSAGE

        chatBody.innerHTML += `

            <div class="bot-message">

                ${data.reply}

            </div>

        `;

        // AUTO SCROLL

        chatBody.scrollTop =
        chatBody.scrollHeight;

    } catch (error) {

        console.log(error);

        // ERROR MESSAGE

        chatBody.innerHTML += `

            <div class="bot-message">

                Server error occurred.

            </div>

        `;
    }
}

// ========================================
// ENTER KEY SUPPORT
// ========================================

document.addEventListener(
    'DOMContentLoaded',
    () => {

    // CHAT INPUT

    const chatInput =
    document.getElementById(
        'chatInput'
    );

    if (chatInput) {

        chatInput.addEventListener(
            'keypress',
            function (e) {

                if (e.key === 'Enter') {

                    sendMessage();
                }
            }
        );
    }

    // SKILLS INPUT

    const skillsInput =
    document.getElementById(
        'skills'
    );

    if (skillsInput) {

        skillsInput.addEventListener(
            'keypress',
            function (e) {

                if (e.key === 'Enter') {

                    findJobs();
                }
            }
        );
    }
});