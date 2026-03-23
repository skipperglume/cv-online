const createNavigationMenu = () => {
    // Get all subpages/sections
    const sections = ['About', 'Main work', 'Hobbies', 'Contact'];

    // Create a navigation menu element
    const nav = document.createElement('nav');
    const ul = document.createElement('ul');

    // Loop through sections and create list items
    sections.forEach(section => {
        const li = document.createElement('li');
        const a = document.createElement('a');
        if (section === 'About') {
            a.href = 'index.html';
        } else {
            a.href = section.toLowerCase().replace(' ', '-') + '.html';
        }
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