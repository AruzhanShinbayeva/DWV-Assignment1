document.addEventListener("DOMContentLoaded", function() {
    // Fetch the JSON file from the server (you will have this file hosted on GitHub Pages or locally)
    fetch("films_data.json")
        .then(response => response.json())
        .then(data => {
            const filmList = document.getElementById("film-list");

            // Function to display the films
            function displayFilms(films) {
                filmList.innerHTML = ''; // Clear existing films

                films.forEach(film => {
                    const filmItem = document.createElement("div");
                    filmItem.classList.add("film-item");

                    filmItem.innerHTML = `
                        <h2>${film.title}</h2>
                        <p><strong>Directed by:</strong> ${film.directed_by}</p>
                        <p><strong>Release Year:</strong> ${film.release_year}</p>
                        <p><strong>Countries:</strong> ${film.countries}</p>
                        <p><strong>Box Office:</strong> $${film.box_office_revenue.toLocaleString()}</p>
                    `;

                    filmList.appendChild(filmItem);
                });
            }

            // Initially display films without sorting
            displayFilms(data);

            // Sorting by Box Office (ascending)
            document.querySelector("#sort-by-box-office-asc").addEventListener("click", function() {
                const sortedByBoxOfficeAsc = [...data].sort((a, b) => a.box_office_revenue - b.box_office_revenue);
                displayFilms(sortedByBoxOfficeAsc);
            });

            // Sorting by Box Office (descending)
            document.querySelector("#sort-by-box-office-desc").addEventListener("click", function() {
                const sortedByBoxOfficeDesc = [...data].sort((a, b) => b.box_office_revenue - a.box_office_revenue);
                displayFilms(sortedByBoxOfficeDesc);
            });

            // Sorting by Release Year (optional, for completeness)
            document.querySelector("#sort-by-year").addEventListener("click", function() {
                const sortedByYear = [...data].sort((a, b) => a.release_year - b.release_year);
                displayFilms(sortedByYear);
            });
        })
        .catch(error => console.error('Error fetching data:', error));
});
