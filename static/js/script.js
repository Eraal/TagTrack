// Sidebar toggle for "Items"
const toggleItems = document.querySelector('.toggle-items');
const submenu = document.querySelector('.submenu');

toggleItems.addEventListener('click', () => {
  submenu.classList.toggle('hidden');
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
