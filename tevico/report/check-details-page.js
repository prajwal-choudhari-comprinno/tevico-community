document.addEventListener('DOMContentLoaded', function () {
    const id = getQueryParam('id');
    if (id) {
        const report = check_reports.find(item => item.name === id);
        if (report) {
            displayCheckDetails(report);
        } else {
            console.error('Report not found for ID:', id);
        }
    } else {
        console.error('No ID parameter provided in URL');
        window.location.href = 'index.html';
    }
});

getQueryParam = (paramName) => {
    try {
        const param = new URLSearchParams(window.location.search).get(paramName);
        if (param === null) {
            throw new Error(`Query parameter '${paramName}' not found`);
        }
        return param;
    } catch (error) {
        console.error('Error getting query parameter:', error.message);
        return null;
    }
}

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