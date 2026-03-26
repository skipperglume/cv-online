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
    document.body.insertBefore(nav, document.body.firstChild);
};

const decodeText = (codes) => String.fromCharCode(...codes);

// Replace the obfuscated placeholder text in the HTML with real email links.
//
// How it works:
// 1. Each email link in the HTML has a `data-email-key` attribute instead of a
//    visible raw email address in the source.
// 2. This function looks up the matching encoded character codes.
// 3. It decodes those codes back into a real email string.
// 4. It updates both the link text and the `mailto:` target in the rendered page.
//
// This does not make the email impossible to harvest, but it avoids exposing the
// plain address directly in the static HTML, which blocks the simplest crawlers.
const hydrateEmailLinks = () => {
    const emailAddresses = {
        cern: [100, 101, 110, 121, 115, 46, 116, 105, 109, 111, 115, 104, 121, 110, 64, 99, 101, 114, 110, 46, 99, 104],
        gmail: [99, 100, 101, 110, 116, 105, 109, 111, 115, 104, 64, 103, 109, 97, 105, 108, 46, 99, 111, 109]
    };

    document.querySelectorAll('[data-email-key]').forEach((link) => {
        const emailKey = link.getAttribute('data-email-key');
        const encodedEmail = emailAddresses[emailKey];

        if (!encodedEmail) {
            return;
        }

        const emailAddress = decodeText(encodedEmail);
        link.href = `mailto:${emailAddress}`;
        link.textContent = emailAddress;
    });
};

const hydratePhoneNumbers = () => {
    const phoneNumbers = {
        primary: [43, 52, 50, 48, 45, 55, 55, 54, 45, 52, 55, 52, 45, 57, 50, 49]
    };

    document.querySelectorAll('[data-phone-key]').forEach((phoneElement) => {
        const phoneKey = phoneElement.getAttribute('data-phone-key');
        const encodedPhone = phoneNumbers[phoneKey];

        if (!encodedPhone) {
            return;
        }

        phoneElement.textContent = decodeText(encodedPhone);
    });
};

const initializePage = () => {
    createNavigationMenu();
    hydrateEmailLinks();
    hydratePhoneNumbers();
};

// The script is loaded near the top of the body, before the email links exist in
// the DOM. Wait until the document is fully parsed, otherwise no links are found
// and the placeholder text remains visible.
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializePage);
} else {
    initializePage();
}