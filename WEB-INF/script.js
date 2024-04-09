const searchInput = document.getElementById('searchInput');
const searchButton = document.getElementById('searchButton');
const searchResults = document.getElementById('searchResults');
const searchBox = document.getElementById('searchBox');

searchButton.addEventListener('click', performSearch);

function performSearch() {
    const query = searchInput.value;
// Make the changes, according to the database. 
    const results = [
        {
            title: 'Result 1',
            url: 'https://example.com/result1',
            summary: 'This is a summary of the first result.'
        },
        {
            title: 'Result 2',
            url: 'https://example.com/result2',
            summary: 'This is a summary of the second result.'
        }
    ];

    displayResults(results);
    searchBox.classList.add('top-left');
}

function displayResults(results) {
    searchResults.innerHTML = '';

    results.forEach(result => {
        const resultDiv = document.createElement('div');
        resultDiv.classList.add('result');

        const title = document.createElement('h3');
        const link = document.createElement('a');
        link.href = result.url;
        link.textContent = result.title;
        title.appendChild(link);

        const summary = document.createElement('p');
        summary.textContent = result.summary;

        resultDiv.appendChild(title);
        resultDiv.appendChild(summary);

        searchResults.appendChild(resultDiv);
    });
}
