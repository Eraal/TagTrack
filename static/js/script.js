// Sidebar toggle for "Items"
document.addEventListener("DOMContentLoaded", function () {
  const toggleItems = document.querySelector(".toggle-items");
  const submenu = document.querySelector(".submenu");

  toggleItems.addEventListener("click", function () {
      submenu.classList.toggle("open");
  });
});


// Filter functionality
const filters = document.querySelectorAll('.filter');

filters.forEach((filter) => {
  filter.addEventListener('change', (event) => {
    const filterValue = event.target.value;
    console.log(`Filter applied: ${filterValue}`); // Add filtering logic here
    alert(`Filtered by: ${filterValue}`);
  });
});
