const theButtons = document.querySelectorAll(".li-btn");

// Add click event listeners to each side navigation button
theButtons.forEach((tab) => {
  tab.addEventListener("click", (event) => {
    const title = document.querySelector(".screen-title");
    const listItems = document.querySelectorAll(".li-btn");
    const divs = document.querySelectorAll(".main-contained > div");

    // Remove 'active' class from all list items and divs
    listItems.forEach((item) => item.classList.remove("active"));
    divs.forEach((div) => div.classList.remove("active"));

    // Add 'active' class to the clicked tab and its corresponding content div
    tab.classList.add("active");
    const pageTitle = tab.querySelector("p");
    title.textContent = pageTitle.innerText;

    const targetDivId = tab.getAttribute("data-target");
    const page = document.getElementById(targetDivId);
    page.classList.add("active");

    // Store the new active page in local storage
    storeActiveSection(targetDivId);
  });
});


// Function to store the active section in local storage
function storeActiveSection(sectionId) {
    localStorage.setItem("activeSection", sectionId);
  }
  
  // Function to get the active section from local storage
  function getActiveSection() {
    return localStorage.getItem("activeSection");
  }
  
  // Function to restore the active section based on stored data in local storage
  function restoreActiveSection() {
    const activeSectionId = getActiveSection();
    if (activeSectionId) {
      const activeTab = document.querySelector(
        `[data-target="${activeSectionId}"]`
      );
      if (activeTab) {
        activeTab.click(); // Trigger click to show the active section
      }
    }
  }
  