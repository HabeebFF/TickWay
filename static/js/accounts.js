// Define arrays for tables
let users = [];
let dbUsers = [];

// Define variables for pagination
const itemsPerPage = 10;
let currentPage = 1;
let totalUsers = 0;
let totalPages = 1;

// Function to populate the account table with users based on pagination
const populateAccountTable = (users, page) => {
  const tbody = document.querySelector("#accountTable tbody");
  tbody.innerHTML = ""; // Clear existing rows

  const startIndex = (page - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const displayedUsers = users.slice(startIndex, endIndex);

  displayedUsers.forEach((user) => {
    const row = document.createElement("tr");

    row.innerHTML = `
      <td>${user.username}</td>
      <td>${user.first_name} ${user.last_name}</td>
      <td>${user.email}</td>
      <td>${user.phone_number}</td>
      <td>${user.balance}</td>
      <td class="status">${user.is_active ? "active" : "inactive"}</td>
      <td><button class="ban-btn" data-id="${user.email}">${user.is_active ? 'Ban' : 'Unban'}</button></td>
    `;

    tbody.appendChild(row);
  });
};

// Function to update pagination info
const updatePaginationInfo = () => {
  document.getElementById("currentPage").textContent = currentPage;
  document.getElementById("totalPages").textContent = totalPages;
};

// Function to handle pagination navigation
const navigatePagination = (direction) => {
  if (direction === "next" && currentPage < totalPages) {
    currentPage++;
  } else if (direction === "prev" && currentPage > 1) {
    currentPage--;
  }

  // Repopulate the account table with users for the updated page
  populateAccountTable(dbUsers, currentPage);
  updatePaginationInfo();
};

// Event listener for next and previous pagination buttons
document
  .querySelector("#nextBtn")
  .addEventListener("click", () => navigatePagination("next"));
document
  .querySelector("#prevBtn")
  .addEventListener("click", () => navigatePagination("prev"));

// Function to filter users based on search input
const filterUsers = (searchInput) => {
  const filteredUsers = dbUsers.filter((user) => {
    const fullName = `${user.first_name} ${user.last_name}`.toLowerCase();
    return fullName.includes(searchInput.toLowerCase());
  });

  // Repopulate the account table with filtered users
  currentPage = 1;
  totalUsers = filteredUsers.length;
  totalPages = Math.ceil(totalUsers / itemsPerPage);
  populateAccountTable(filteredUsers, currentPage);
  updatePaginationInfo();
};

// Event listener for search form submission
document.getElementById("search-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const searchInput = event.target.querySelector("input").value;
  filterUsers(searchInput);
});

// Event listener for search input changes
document.getElementById("search-form").addEventListener("input", (event) => {
  const searchInput = event.target.value;
  filterUsers(searchInput);
});

// Function to handle refresh button click
const handleRefresh = () => {
  const rfElement = document.getElementById("rf-btn");
  const rfpState = rfElement.previousElementSibling;
  rfElement.style.animation = "rotate 1s infinite";
  rfpState.textContent = "Getting...";

  fetchUsers().then(() => {
    rfpState.textContent = "Up to date";
    rfElement.style.animation = "none";
    setTimeout(() => {
      rfpState.textContent = "";
    }, 2000);

    // Repopulate the account table with users for the current page
    populateAccountTable(dbUsers, currentPage);
  });
};

document.getElementById("rf-btn").addEventListener("click", handleRefresh);

// Event listener for ban buttons
document.querySelector("#accountTable").addEventListener("click", (event) => {
  if (event.target.classList.contains("ban-btn")) {
    const button = event.target;
    const userId = button.dataset.email;
    const statusCell = button.closest("tr").querySelector(".status");

    if (statusCell.textContent === "inactive") {
      // Confirm the user's intention to unban
      if (confirm("Are you sure you want to unban this user?")) {
        // Simulate a successful unban operation for demonstration purposes
        setTimeout(() => {
          alert("User unbanned successfully.");
          // Update the table or any other necessary action
          statusCell.textContent = "active";
          button.textContent = "Ban";
          button.style.backgroundColor = "red";
        }, 1000);
      }
    } else {
      // Confirm the user's intention to ban
      if (confirm("Are you sure you want to ban this user?")) {
        // Simulate a successful ban operation for demonstration purposes
        setTimeout(() => {
          alert("User banned successfully.");
          // Update the table or any other necessary action
          statusCell.textContent = "inactive";
          button.textContent = "Unban";
          button.style.backgroundColor = "green";
        }, 1000);
      }
    }

    // Commented out fetch API to send status to backend
    /*
      fetch(`/api/users/${userId}/status`, {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({ status: statusCell.textContent }),
      })
      .then(response => response.json())
      .then(data => {
          console.log('Success:', data);
      })
      .catch((error) => {
          console.error('Error:', error);
      });
    */
  }
});

// Function for Tickets
const fetchTickets = async () => {
  const targetUrl = '/get_all_tickets/'

  try {
    const response = await fetch(targetUrl, {
      method: 'GET'
    });
    const result = await response.json();
    const tickets = result.tickets;
  } catch (error) {
    
  }
}


const fetchUsers = async () => {
  try {
    // const proxyUrl = 'https://cors-anywhere.herokuapp.com/';
    const targetUrl = '/get_all_users/';

    const response = await fetch(targetUrl, {
      method: 'GET'
    });

    const result = await response.json();
    const users = result.users; // Extract the users array from the response
    const wallets = result.wallet; // Extract the wallets array from the response
    console.log(users, wallets);

    // Merge the users and wallets data
    dbUsers = users.map(user => {
      const wallet = wallets.find(w => w.user_id === user.user_id);
      return {
        ...user,
        balance: wallet ? wallet.wallet_balance : '0.00'
      };
    });

    totalUsers = dbUsers.length;
    totalPages = Math.ceil(totalUsers / itemsPerPage);
    populateAccountTable(dbUsers, currentPage);
    updatePaginationInfo();
  } catch (error) {
    console.error('Error fetching users:', error);
  }
};

// Call the fetchUsers function
fetchUsers();



// Get Total
var userTotal;