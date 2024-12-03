import { setActiveNavLink, getQueryParam } from './utils/utils.js';

document.addEventListener('DOMContentLoaded', function () {
    const source = getQueryParam('from');
    const id = getQueryParam('id');

    const backArrow = document.getElementById('backButton');
    const firstBreadcrumb = document.querySelector('.breadcrumb-item:first-child');

    const navigationMap = {
        'browse': {
            href: './browse.html',
            text: 'Browse Checks'
        },
        'war': {
            href: './well-architected-review.html',
            text: 'Well-Architected Review'
        }
    };

    if (id) {
        setActiveNavLink();
        const report = check_reports.find(item => item.name === id);
        if (report) {
            displayCheckDetails(report);
            if (source && navigationMap[source]) {
                const { href, text } = navigationMap[source];
                const sectionParam = source === 'war' && report.section ? `?section=${report.section}` : '';
                backArrow.href = `${href}${sectionParam}`;
                firstBreadcrumb.innerHTML = `<a href="${href}${sectionParam}">${text}</a>`;
            }
        } else {
            console.error('Report not found for ID:', id);
        }
    } else {
        console.error('No ID parameter provided in URL');
        window.location.href = 'index.html';
    }
});

function displayCheckDetails(report) {
    const updateElement = (id, value) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value || '-';
        }
    };

    const { check_metadata: meta = {} } = report;

    updateElement('page_title', meta.check_id);
    updateElement('framework_text', report.framework);
    updateElement('check_title_text', meta.check_title);
    updateElement('check_id_text', meta.check_id);
    updateElement('description_text', meta.description);
    updateElement('resource_id_template_text', meta.resource_id_template);
    updateElement('resource_type_text', meta.resource_type);
    updateElement('risk_text', meta.risk);
    updateElement('service_name_text', meta.service_name);
    updateElement('severity_text', meta.severity);
}