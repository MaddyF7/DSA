// Loads DOM
document.addEventListener('DOMContentLoaded', () => {
    console.log('Page Loaded: JavaScript is connected!');

    // Confirm delete
    document.body.addEventListener('click', (event) => {
        if (event.target && event.target.classList.contains('delete-button')) {
            console.log('Delete button clicked:', event.target);
            const confirmDelete = confirm('Are you sure you want to delete this record?');
            if (!confirmDelete) {
                event.preventDefault();
            }
        }
    });

    // Auto-dismiss flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach((alert) => {
        setTimeout(() => {
            alert.classList.add('fade');
            setTimeout(() => {
                alert.remove();
            }, 500); // Transition duration matches CSS
        }, 5000); // 5 seconds delay
    });

    // Filter function on pages
    function applyFilter(tableBodyId, filters) {
        const rows = document.querySelectorAll(`#${tableBodyId} tr`);

        rows.forEach(row => {
            let isVisible = true;

            filters.forEach(filter => {
                const columnIndex = filter.columnIndex;
                const filterValue = filter.value.toLowerCase();
                const cellText = row.cells[columnIndex]?.textContent.toLowerCase() || '';

                if (filterValue && !cellText.includes(filterValue)) {
                    isVisible = false;
                }
            });

            row.style.display = isVisible ? '' : 'none';
        });
    }

    // Filter functionality for exams.html
    const filterExamButton = document.getElementById('apply-filter');
    if (filterExamButton && document.getElementById('exam-table-body')) {
        filterExamButton.addEventListener('click', () => {
            const filterUser = document.getElementById('filter-user').value.toLowerCase();
            const filterExam = document.getElementById('filter-exam').value.toLowerCase();

            applyFilter('exam-table-body', [
                { columnIndex: 0, value: filterUser }, // Apprentice column
                { columnIndex: 1, value: filterExam } // Exam Name column
            ]);
        });
    }

    // Filter functionality for leave.html
    const filterLeaveButton = document.getElementById('apply-filter');
    if (filterLeaveButton && document.getElementById('leave-table-body')) {
        filterLeaveButton.addEventListener('click', () => {
            const filterApprentice = document.getElementById('filter-apprentice').value.toLowerCase();

            applyFilter('leave-table-body', [
                { columnIndex: 0, value: filterApprentice } // Apprentice column
            ]);
        });
    }

    // Filter functionality for projects.html
    const filterProjectButton = document.getElementById('apply-filter');
    if (filterProjectButton && document.getElementById('project-table-body')) {
        filterProjectButton.addEventListener('click', () => {
            const filterApprentice = document.getElementById('filter-apprentice').value.toLowerCase();
            const filterProject = document.getElementById('filter-project').value.toLowerCase();

            applyFilter('project-table-body', [
                { columnIndex: 0, value: filterApprentice }, // Apprentice column
                { columnIndex: 1, value: filterProject } // Project Name column
            ]);
        });
    }

    // Ensure user enters email and password on login.html form
    const loginForm = document.querySelector('form');
    if (loginForm) {
        loginForm.addEventListener('submit', (event) => {
            const email = document.querySelector('#email').value.trim();
            const password = document.querySelector('#password').value.trim();

            if (!email || !password) {
                event.preventDefault();
                alert('Email and Password are required.');
            }
        });
    }

    // Toggle apprentice fields visibility based on role selection and manage required attributes
    const roleSelect = document.getElementById('role');
    const apprenticeFields = document.getElementById('apprentice-fields');
    const cohortField = document.getElementById('cohort');
    const startDateField = document.getElementById('start_date');
    const lineManagerField = document.getElementById('line_manager_id');

    if (roleSelect) {
        roleSelect.addEventListener('change', () => {
            if (roleSelect.value === 'apprentice') {
                apprenticeFields.style.display = 'block';
                // Set apprentice fields as required
                cohortField.setAttribute('required', 'required');
                startDateField.setAttribute('required', 'required');
                lineManagerField.setAttribute('required', 'required');
            } else {
                apprenticeFields.style.display = 'none';
                // Remove required attribute from apprentice fields
                cohortField.removeAttribute('required');
                startDateField.removeAttribute('required');
                lineManagerField.removeAttribute('required');
            }
        });
    }
});