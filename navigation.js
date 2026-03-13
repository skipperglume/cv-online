const createNavigationMenu = () => {
    // Get all subpages/sections (dummy data for demonstration, replace with actual sections)
    const sections = ['Home', 'About', 'Services', 'Contact'];

    // Create a navigation menu element
    const nav = document.createElement('nav');
    const ul = document.createElement('ul');

    // Loop through sections and create list items
    sections.forEach(section => {
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.href = `#${section.toLowerCase()}`; // Assuming sections are linked by ID
        a.textContent = section;
        li.appendChild(a);
        ul.appendChild(li);
    });

    // Append the list to the nav
    nav.appendChild(ul);

    // Append the navigation menu to the body (or a specific container)
    document.body.appendChild(nav);
};

// Call the function to create the menu
createNavigationMenu();