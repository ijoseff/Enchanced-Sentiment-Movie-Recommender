new autoComplete({
    data: {                              
        src: films,                       // Data source [Array, Function, Async]
    },
    selector: "#autoComplete",            // Input field selector
    threshold: 2,                         // Min. characters to start search
    debounce: 100,                        // Delay before searching
    searchEngine: "strict",               // Search mode
    resultsList: {                        
        render: true,
        container: source => {
            source.setAttribute("id", "autoComplete_list"); // Correct ID for results list
        },
        destination: document.querySelector("#autoComplete"),
        position: "afterend",
        element: "ul"
    },
    maxResults: 5,                         // Limit displayed results
    highlight: true,                       // Highlight matches
    resultItem: {                         
        content: (data, source) => {
            source.innerHTML = data.match; // Display matched text
        },
        element: "li"
    },
    noResults: () => {                    
        const result = document.createElement("li");
        result.setAttribute("class", "no_result");
        result.setAttribute("tabindex", "1");
        result.textContent = "No Results"; // Use textContent for better performance and security
        const resultList = document.querySelector("#autoComplete_list");
        if (resultList) {
            resultList.appendChild(result);
        }
    },
    onSelection: feedback => {           
        const input = document.getElementById("autoComplete");
        if (input) {
            input.value = feedback.selection.value; // Populate selected value in input
        }
    }
});
