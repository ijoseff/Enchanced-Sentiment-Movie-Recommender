$(function () {
  // Enable/disable button based on input field
  $('#autoComplete').on('input', function () {
    const input = $(this).val().trim();
    $('.movie-button').attr('disabled', input === '');
  });

  // Button click event
  $('.movie-button').on('click', function () {
    const apiKey = '008a5040d287806328d4c383f9d3fbab';
    const title = $('.movie').val().trim();

    if (!title) {
      displayMessage('fail');
      return;
    }
    loadDetails(apiKey, title);
  });
});

// Handle movie recommendation card click
function recommendCard(e) {
  const apiKey = '008a5040d287806328d4c383f9d3fbab';
  const title = e.getAttribute('title');
  loadDetails(apiKey, title);
}

// Load movie details
async function loadDetails(apiKey, title) {
  try {
    showLoader();
    const url = `https://api.themoviedb.org/3/search/movie?api_key=${apiKey}&query=${encodeURIComponent(title)}`;
    const response = await fetch(url);
    const movieData = await response.json();

    if (!movieData.results || movieData.results.length === 0) {
      displayMessage('fail');
      return;
    }

    const bestMatch = findBestMatch(movieData.results, title);
    getMovieDetails(apiKey, bestMatch.id, bestMatch.title, bestMatch.original_title);
  } catch (error) {
    console.error('Error fetching movie details:', error);
    alert('Failed to fetch movie details. Please try again.');
  } finally {
    hideLoader();
  }
}

// Find the closest matching movie
function findBestMatch(results, title) {
  const exactMatch = results.find(movie => movie.original_title === title);
  if (exactMatch) return exactMatch;

  const matches = results.map(movie => ({
    ...movie,
    similarity: similarity(title, movie.original_title),
  }));
  return matches.reduce((best, current) => (current.similarity > best.similarity ? current : best));
}

// Fetch full movie details
async function getMovieDetails(apiKey, movieId, title, originalTitle) {
  try {
    showLoader();
    const url = `https://api.themoviedb.org/3/movie/${movieId}?api_key=${apiKey}`;
    const response = await fetch(url);
    const movieDetails = await response.json();
    displayMovieDetails(movieDetails, title, originalTitle);
  } catch (error) {
    console.error('Error fetching movie details:', error);
    alert('Failed to load movie details.');
  } finally {
    hideLoader();
  }
}

// Display movie details in the UI
function displayMovieDetails(details, title, originalTitle) {
  // Populate the results area with movie details
  $('.results').css('display', 'block');
  $('.fail').css('display', 'none');
  console.log('Movie Details:', details, title, originalTitle);
  // Populate details here as per the requirements
}

// Similarity calculation using Levenshtein distance
function similarity(s1, s2) {
  const longer = s1.length >= s2.length ? s1 : s2;
  const shorter = s1.length < s2.length ? s1 : s2;
  const longerLength = longer.length;
  if (longerLength === 0) return 1.0;

  const distance = editDistance(longer, shorter);
  return (longerLength - distance) / longerLength;
}

// Calculate edit distance
function editDistance(s1, s2) {
  const costs = Array(s2.length + 1).fill(0).map((_, i) => i);

  for (let i = 1; i <= s1.length; i++) {
    let lastValue = i;
    for (let j = 1; j <= s2.length; j++) {
      const newValue = s1[i - 1] === s2[j - 1]
        ? costs[j - 1]
        : Math.min(costs[j - 1], lastValue, costs[j]) + 1;
      costs[j - 1] = lastValue;
      lastValue = newValue;
    }
    costs[s2.length] = lastValue;
  }
  return costs[s2.length];
}

// Utility functions
function displayMessage(type) {
  if (type === 'fail') {
    $('.fail').css('display', 'block');
    $('.results').css('display', 'none');
  }
}

function showLoader() {
  $('#loader').fadeIn();
}

function hideLoader() {
  $('#loader').fadeOut();
}
