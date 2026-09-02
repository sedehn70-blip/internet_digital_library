// Admin Dashboard Pagination and Filtering

// Initialize DataTables for better table management
$(document).ready(function() {
    // Initialize DataTable for users table
    $('#usersTable').DataTable({
        "language": {
            "url": "//cdn.datatables.net/plug-ins/1.10.25/i18n/Persian.json"
        },
        "order": [[0, "asc"]],
        "pageLength": 10,
        "lengthMenu": [10, 25, 50, 100]
    });

    // Initialize DataTable for active readers table
    $('#activeReadersTable').DataTable({
        "language": {
            "url": "//cdn.datatables.net/plug-ins/1.10.25/i18n/Persian.json"
        },
        "order": [[1, "desc"]],
        "pageLength": 5
    });

    // Initialize date range picker
    $('input[name="datefilter"]').daterangepicker({
        autoUpdateInput: false,
        locale: {
            cancelLabel: 'پاک کردن',
            applyLabel: 'اعمال',
            fromLabel: 'از',
            toLabel: 'تا',
            customRangeLabel: 'انتخاب تاریخ',
            daysOfWeek: ['ی', 'د', 'س', 'چ', 'پ', 'ج', 'ش'],
            monthNames: ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'],
            firstDay: 6
        },
        opens: 'right'
    });

    $('input[name="datefilter"]').on('apply.daterangepicker', function(ev, picker) {
        $(this).val(picker.startDate.format('YYYY/MM/DD') + ' - ' + picker.endDate.format('YYYY/MM/DD'));
        // Trigger filter update
        updateFilters();
    });

    $('input[name="datefilter"]').on('cancel.daterangepicker', function(ev, picker) {
        $(this).val('');
        // Trigger filter update
        updateFilters();
    });

    // Save report configuration
    $('#saveReportBtn').on('click', function() {
        const reportName = $('#reportName').val();
        if (!reportName) {
            alert('لطفاً نامی برای گزارش وارد کنید.');
            return;
        }
        
        // Get current filter values
        const filters = {
            dateRange: $('input[name="datefilter"]').val(),
            // Add more filters as needed
        };
        
        // Save to localStorage
        const savedReports = JSON.parse(localStorage.getItem('savedReports') || '[]');
        savedReports.push({
            name: reportName,
            filters: filters,
            createdAt: new Date().toISOString()
        });
        localStorage.setItem('savedReports', JSON.stringify(savedReports));
        
        // Update saved reports list
        updateSavedReportsList();
        
        // Close modal
        $('#saveReportModal').modal('hide');
        $('#reportName').val('');
    });

    // Load saved reports on page load
    updateSavedReportsList();
});

// Update filters and refresh data
function updateFilters() {
    // Show loading state
    $('#loadingIndicator').show();
    
    // Get filter values
    const dateRange = $('input[name="datefilter"]').val();
    
    // Build URL with filters
    let url = new URL(window.location.href);
    
    if (dateRange) {
        const [startDate, endDate] = dateRange.split(' - ');
        url.searchParams.set('start_date', startDate);
        url.searchParams.set('end_date', endDate);
    } else {
        url.searchParams.delete('start_date');
        url.searchParams.delete('end_date');
    }
    
    // Reload page with new filters
    window.location.href = url.toString();
}

// Update saved reports list in the dropdown
function updateSavedReportsList() {
    const savedReports = JSON.parse(localStorage.getItem('savedReports') || '[]');
    const $savedReportsList = $('#savedReportsList');
    
    // Clear existing items
    $savedReportsList.empty();
    
    if (savedReports.length === 0) {
        $savedReportsList.append('<a class="dropdown-item" href="#">گزارش ذخیره‌شده‌ای وجود ندارد</a>');
        return;
    }
    
    // Sort by creation date (newest first)
    savedReports.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    
    // Add each report to the dropdown
    savedReports.forEach((report, index) => {
        const date = new Date(report.createdAt).toLocaleDateString('fa-IR');
        $savedReportsList.append(`
            <div class="dropdown-item d-flex justify-content-between align-items-center">
                <a href="#" class="load-report" data-index="${index}">
                    ${report.name}
                    <small class="text-muted d-block">${date}</small>
                </a>
                <button class="btn btn-sm btn-outline-danger delete-report" data-index="${index}">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `);
    });
    
    // Add event listeners for loading and deleting reports
    $('.load-report').on('click', function(e) {
        e.preventDefault();
        const index = $(this).data('index');
        loadReport(savedReports[index]);
    });
    
    $('.delete-report').on('click', function(e) {
        e.stopPropagation();
        const index = $(this).data('index');
        deleteReport(index);
    });
}

// Load a saved report
function loadReport(report) {
    // Apply filters from the saved report
    if (report.filters.dateRange) {
        $('input[name="datefilter"]').val(report.filters.dateRange);
    }
    
    // Update the UI to reflect the loaded filters
    // Then trigger the filter update
    updateFilters();
}

// Delete a saved report
function deleteReport(index) {
    if (!confirm('آیا از حذف این گزارش اطمینان دارید؟')) {
        return;
    }
    
    const savedReports = JSON.parse(localStorage.getItem('savedReports') || '[]');
    savedReports.splice(index, 1);
    localStorage.setItem('savedReports', JSON.stringify(savedReports));
    
    // Update the UI
    updateSavedReportsList();
}

// Export to Excel
function exportToExcel(tableId, fileName) {
    const table = document.getElementById(tableId);
    const ws = XLSX.utils.table_to_sheet(table);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'گزارش');
    XLSX.writeFile(wb, `${fileName}.xlsx`);
}
