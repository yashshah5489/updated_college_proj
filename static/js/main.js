document.addEventListener('DOMContentLoaded', function() {
    // Auto dismiss flash messages after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Add tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Enhance textarea to auto-expand as user types
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(function(textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });

    // Analyzer page - format code and bullets in analysis
    const analysisContent = document.querySelector('.analysis-content');
    if (analysisContent) {
        // Add syntax highlighting to code blocks
        const content = analysisContent.innerHTML;
        const formattedContent = content
            // Format bullet points
            .replace(/- /g, '• ')
            // Format numbered lists
            .replace(/(\d+)\. /g, '<strong>$1.</strong> ')
            // Format headers
            .replace(/## (.*?)(<br>|$)/g, '<h5>$1</h5>')
            .replace(/# (.*?)(<br>|$)/g, '<h4>$1</h4>');
        
        analysisContent.innerHTML = formattedContent;
    }

    // History page - enhance table with sorting and searching
    const historyTable = document.querySelector('.history-card table');
    if (historyTable) {
        // Add search functionality
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.placeholder = 'Search your analyses...';
        searchInput.className = 'form-control mb-3';
        
        historyTable.parentNode.insertBefore(searchInput, historyTable);
        
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const rows = historyTable.querySelectorAll('tbody tr');
            
            rows.forEach(function(row) {
                const query = row.cells[1].textContent.toLowerCase();
                if (query.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
});
