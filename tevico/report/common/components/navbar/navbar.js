function loadNavbar() {
  return fetch('./common/components/navbar/navbar.html')
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to load navbar component');
      }
      return response.text();
    })
    .then(html => {
      const pageWrapper = document.querySelector('.page-wrapper');
      if (pageWrapper) {
        pageWrapper.insertAdjacentHTML('afterbegin', html);
        initNavbar();
        return html;
      } else {
        throw new Error('Page wrapper element not found');
      }
    })
    .catch(error => {
      console.error('Error loading navbar:', error);
    });
}

function initNavbar() {

  const storedAccountId = localStorage.getItem('accountId');
  const storedAccountName = localStorage.getItem('accountName');

  if (storedAccountId && storedAccountName) {
    updateAccountInfo(storedAccountId, storedAccountName);
  }
}

function updateAccountInfo(accountId, accountName) {
  const accountIdElement = document.getElementById('accountId');
  const accountNameElement = document.getElementById('accountName');

  if (accountIdElement) {
    accountIdElement.textContent = accountId;
  }

  if (accountNameElement) {
    accountNameElement.textContent = accountName !== 'Unknown' ? accountName : '--';
  }

  localStorage.setItem('accountId', accountId);
  localStorage.setItem('accountName', accountName);
}

window.updateNavbarAccountInfo = updateAccountInfo;

document.addEventListener('DOMContentLoaded', loadNavbar);