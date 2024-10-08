const repoUrl = document.getElementById('repo-url');
const submitBtn = document.getElementById('submit-btn');
const resultContainer = document.getElementById('result-container');
const previewContent = document.getElementById('preview-content');
const codeContent = document.getElementById('code-content');
const copyBtn = document.getElementById('copy-btn');
const tabButtons = document.querySelectorAll('.tab-button');

submitBtn.addEventListener('click', async () => {
    const language = document.querySelector('input[name="language"]:checked').value;
    const readmeType = document.querySelector('input[name="readme-type"]:checked').value;
    const endpoint = readmeType === 'existing' ? '/showReadme' : '/conjureReadme';

    try {
        const response = await fetch(`http://localhost:9999${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                url: repoUrl.value,
                language: language
            })
        });
        
        const data = await response.text();
        
        // Decode the response if it's not already in UTF-8
        const decodedData = new TextDecoder('utf-8').decode(new TextEncoder().encode(data));
        
        // Update content
        previewContent.innerHTML = marked.parse(decodedData);
        codeContent.textContent = decodedData;
        
        // Show result container
        resultContainer.style.display = 'block';
    } catch (error) {
        console.error('Error:', error);
        alert('README를 생성하는 동안 오류가 발생했습니다');
    }
});

// Tab switching
tabButtons.forEach(button => {
    button.addEventListener('click', () => {
        // Update active tab
        tabButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        
        // Show/hide content
        const tabName = button.getAttribute('data-tab');
        previewContent.classList.toggle('active-content', tabName === 'preview');
        codeContent.classList.toggle('active-content', tabName === 'code');
        
        // Show/hide copy button
        copyBtn.style.display = tabName === 'code' ? 'block' : 'none';
    });
});

// Copy functionality
copyBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(codeContent.textContent)
        .then(() => {
            const originalText = copyBtn.textContent;
            copyBtn.textContent = 'Copied!';
            setTimeout(() => {
                copyBtn.textContent = originalText;
            }, 2000);
        })
        .catch(err => {
            console.error('Failed to copy text:', err);
            alert('Failed to copy text');
        });
});