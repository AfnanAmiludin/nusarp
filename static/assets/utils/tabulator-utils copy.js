/**
 * Advanced Global Tabulator Search Utilities
 * Provides enhanced search and filtering capabilities for Tabulator tables
 */

// Create global namespace for our application
const AppUtils = window.AppUtils || {};

// Advanced Tabulator search utilities namespace
AppUtils.AdvancedTableSearch = {
  // Configuration for advanced search
  config: {
    rowHeight: 32,
    defaultRowsPerPage: 10,
    searchDebounceTime: 300, // milliseconds
  },

  // DOM element selectors
  selectors: {
    searchInput: '#advanced-search-input',
    clearSearchBtn: '#clear-advanced-search',
    activeFiltersContainer: '#active-advanced-filters',
    searchSuggestions: '#advanced-search-suggestions',
  },

  // Utility functions
  utils: {
    // Escape special characters for regex
    escapeRegExp: function(string) {
      return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    },

    // Debounce function to limit search frequency
    debounce: function(func, wait) {
      let timeout;
      return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => {
          func.apply(context, args);
        }, wait);
      };
    }
  },

    // Formatters for cells
    formatters: {
      /**
       * Custom formatter that highlights search matches
       * @param {CellComponent} cell - The cell component
       * @param {Object} formatterParams - The formatter parameters
       * @param {Function} onRendered - Callback function when rendering is complete
       * @returns {string} - The formatted cell value
       */
      highlightFormatter: function(cell, formatterParams, onRendered) {
        let value = cell.getValue();
        
        if (!value || typeof value !== 'string') {
          return value;
        }
        
        // Get search state from global object
        const searchState = AppUtils.TableUtils.searchState;
        let currentSearchTerm = searchState.currentSearchTerm;
        let hasActiveFilters = Object.keys(searchState.groupedFilters).length > 0;
        
        if (!hasActiveFilters && !currentSearchTerm) {
          return value; // Return original value without highlighting
        }
        
        // Apply highlighting for active filters
        if (hasActiveFilters) {
          Object.values(searchState.groupedFilters).forEach((filter) => {
            filter.values.forEach((term) => {
              if (term && term.length > 0) {
                let regex = new RegExp(`(${AppUtils.TableUtils.escapeRegExp(term)})`, 'gi');
                value = value.replace(
                  regex,
                  '<span class="search-highlight">$1</span>'
                );
              }
            });
          });
        }
        
        return value;
      },
  
      /**
       * Custom formatter for actions dropdown with vertical dots
       * @param {CellComponent} cell - The cell component
       * @param {Object} formatterParams - The formatter parameters
       * @param {Function} onRendered - Callback function when rendering is complete
       * @returns {string} - The formatted cell value
       */
      actionsFormatter: function(cell, formatterParams, onRendered) {
        return `
          <div class="dropdown-action">
            <button class="action-btn">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                <path d="M9.5 13a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0zm0-5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0zm0-5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0z"/>
              </svg>
            </button>
            <div class="dropdown-content">
              <a href="#" class="edit-btn">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" class="mr-2" viewBox="0 0 16 16">
                  <path d="M12.854.146a.5.5 0 0 0-.707 0L10.5 1.793 14.207 5.5l1.647-1.646a.5.5 0 0 0 0-.708l-3-3zm.646 6.061L9.793 2.5 3.293 9H3.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.207l6.5-6.5zm-7.468 7.468A.5.5 0 0 1 6 13.5V13h-.5a.5.5 0 0 1-.5-.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.5-.5V10h-.5a.499.499 0 0 1-.175-.032l-.179.178a.5.5 0 0 0-.11.168l-2 5a.5.5 0 0 0 .65.65l5-2a.5.5 0 0 0 .168-.11l.178-.178z"/>
                </svg>
                Edit
              </a>
              <a href="#" class="delete-btn">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" class="mr-2" viewBox="0 0 16 16">
                  <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                  <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                </svg>
                Delete
              </a>
            </div>
          </div>
        `;
      }
    },

  // Advanced search state management
  searchState: {
    currentSearchTerm: '',
    activeFilters: {},
  },

  // Advanced search operators
  operators: {
    // Exact match
    '=': (value, searchTerm) => String(value).trim() === String(searchTerm).trim(),
    
    // Not equal
    '!=': (value, searchTerm) => String(value).trim() !== String(searchTerm).trim(),
    
    // Substring match (case-insensitive)
    'like': (value, searchTerm) => 
      String(value).toLowerCase().includes(String(searchTerm).toLowerCase()),
    
    // Exclude substring
    'not like': (value, searchTerm) => 
      !String(value).toLowerCase().includes(String(searchTerm).toLowerCase()),
    
    // Numeric/string comparisons
    '>': (value, searchTerm) => {
      const numValue = parseFloat(value);
      const numSearchTerm = parseFloat(searchTerm);
      
      if (!isNaN(numValue) && !isNaN(numSearchTerm)) {
        return numValue > numSearchTerm;
      }
      
      return String(value) > String(searchTerm);
    },
    
    // Greater than or equal
    '>=': (value, searchTerm) => {
      const numValue = parseFloat(value);
      const numSearchTerm = parseFloat(searchTerm);
      
      if (!isNaN(numValue) && !isNaN(numSearchTerm)) {
        return numValue >= numSearchTerm;
      }
      
      return String(value) >= String(searchTerm);
    },
    
    // Less than
    '<': (value, searchTerm) => {
      const numValue = parseFloat(value);
      const numSearchTerm = parseFloat(searchTerm);
      
      if (!isNaN(numValue) && !isNaN(numSearchTerm)) {
        return numValue < numSearchTerm;
      }
      
      return String(value) < String(searchTerm);
    },
    
    // Less than or equal
    '<=': (value, searchTerm) => {
      const numValue = parseFloat(value);
      const numSearchTerm = parseFloat(searchTerm);
      
      if (!isNaN(numValue) && !isNaN(numSearchTerm)) {
        return numValue <= numSearchTerm;
      }
      
      return String(value) <= String(searchTerm);
    },
    
    // Starts with
    'starts with': (value, searchTerm) => 
      String(value).toLowerCase().startsWith(String(searchTerm).toLowerCase()),
    
    // Ends with
    'ends with': (value, searchTerm) => 
      String(value).toLowerCase().endsWith(String(searchTerm).toLowerCase())
  },

  /**
   * Parse search term with advanced operators
   * @param {string} searchTerm - Input search term
   * @returns {Object} Parsed search configuration
   */
  parseSearchTerm: function(searchTerm) {
    // Trim and handle whitespace
    searchTerm = String(searchTerm).trim();
    
    // Regex to detect operator prefixes
    const operatorRegex = /^(!=|>=|<=|>|<|like|not like|starts with|ends with|=)\s+(.+)$/i;
    const match = searchTerm.match(operatorRegex);
    
    // If an operator is found, use it; otherwise default to 'like'
    if (match) {
      return {
        operator: match[1].toLowerCase(),
        value: match[2].trim()
      };
    }
    
    // Default to 'like' search
    return {
      operator: 'like',
      value: searchTerm
    };
  },

  /**
   * Find matching values across table columns
   * @param {Array} tableData - Full table data
   * @param {string} searchValue - Search input
   * @param {Array} searchableColumns - Columns to search
   * @returns {Array} Matching search results
   */
  findMatchingValues: function(tableData, searchValue, searchableColumns) {
    if (!searchValue) return [];

    const results = [];
    const { operator, value } = this.parseSearchTerm(searchValue);

    // Search through each specified column
    searchableColumns.forEach((column) => {
      const field = column.field;
      const title = column.title;

      // Collect unique matching values
      const matchingValues = new Set();

      // Recursive search through data and children
      function searchData(data) {
        if (
          data[field] !== undefined &&
          data[field] !== null &&
          this.operators[operator](data[field], value)
        ) {
          matchingValues.add(String(data[field]));
        }

        // Recursively search children if exists
        if (data._children && data._children.length) {
          data._children.forEach((child) => searchData(child));
        }
      }

      // Process all rows
      tableData.forEach((row) => searchData(row));

      // Add matches to results
      matchingValues.forEach((matchValue) => {
        results.push({
          field,
          title,
          value: matchValue,
          operator
        });
      });
    });

    return results;
  },

  /**
   * Create table initialization method with advanced search
   * @param {string} tableSelector - CSS selector for table container
   * @param {Array} tableData - Table data array
   * @param {Array} columnDefs - Column definitions
   * @param {Object} options - Additional Tabulator options
   * @returns {Object} Initialized table with search methods
   */
  initializeTable: function(tableSelector, tableData, columnDefs, options) {
    // Store DOM elements
    const elements = {
      tableContainer: document.querySelector(tableSelector),
      searchInput: document.querySelector(this.selectors.searchInput),
      clearSearchBtn: document.querySelector(this.selectors.clearSearchBtn),
      activeFiltersContainer: document.querySelector(this.selectors.activeFiltersContainer),
      searchSuggestions: document.querySelector(this.selectors.searchSuggestions)
    };
    
    // Default table options
    const defaultOptions = {
      dataTree: true,
      dataTreeChildIndent: 20,
      dataTreeStartExpanded: false,
      layout: 'fitColumns',
      responsiveLayout: 'collapse',
      width: '100%',
      rowHeight: this.config.rowHeight,
      dataTreeExpandElement: "<span class='mr-2'><i class='ti ti-chevron-right'></i></span>",
      dataTreeCollapseElement: "<span class='mr-2'><i class='ti ti-chevron-down'></i></span>",
      dataTreeChildColumnCalcs: false
    };
    
    // Merge options
    const tableOptions = {
      ...defaultOptions, 
      ...options, 
      data: tableData, 
      columns: columnDefs
    };
    
    // Create Tabulator instance
    const table = new Tabulator(tableSelector, tableOptions);
    
    // Define searchable columns (exclude action columns)
    const searchableColumns = columnDefs.filter(col => col.field !== 'actions');
    
    /**
     * Position search suggestions dropdown
     */
    function positionSuggestions() {
      const inputRect = elements.searchInput.getBoundingClientRect();
      const suggestionsElem = $(elements.searchSuggestions);

      suggestionsElem.css({
        position: 'absolute',
        top: inputRect.bottom + window.scrollY + 'px',
        left: inputRect.left + window.scrollX + 'px',
        width: inputRect.width + 'px',
      });
    }
    
    /**
     * Show search suggestions
     * @param {string} searchValue - Current search input
     */
    function showSuggestions(searchValue) {
      const { operator, value } = AppUtils.AdvancedTableSearch.parseSearchTerm(searchValue);
      const results = AppUtils.AdvancedTableSearch.findMatchingValues(tableData, searchValue, searchableColumns);
  
      // Clear previous suggestions
      $(elements.searchSuggestions).empty();
  
      if (results.length > 0) {
        // Group results by column
        const groupedResults = {};
        results.forEach((result) => {
          if (!groupedResults[result.field]) {
            groupedResults[result.field] = [];
          }
          groupedResults[result.field].push(result);
        });
  
        // Add column headers and values
        Object.keys(groupedResults).forEach((field) => {
          const fieldResults = groupedResults[field];
          const columnTitle = fieldResults[0].title;
  
          // Add column header
          $(elements.searchSuggestions).append(`
            <div class="px-3 py-1 text-xs text-gray-500 bg-gray-100">${columnTitle}</div>
          `);
  
          // Add values
          fieldResults.forEach((result) => {
            const displayValue = result.operator !== 'like' 
              ? `${result.operator} ${result.value}` 
              : result.value;
  
            $(elements.searchSuggestions).append(`
              <div class="suggestion-item px-3 py-2 hover:bg-gray-100 cursor-pointer"
                  data-field="${result.field}"
                  data-value="${displayValue}"
                  data-title="${result.title}">
                <span class="search-highlight">${displayValue}</span>
              </div>
            `);
          });
        });
  
        // Show suggestions
        $(elements.searchSuggestions).removeClass('hidden');
        positionSuggestions();
      } else {
        $(elements.searchSuggestions).addClass('hidden');
      }
    }
    
    /**
     * Update active filter badges
     */
    function updateFilterBadges() {
      const searchState = AppUtils.AdvancedTableSearch.searchState;
      
      // Clear existing badges
      $(elements.activeFiltersContainer).empty();
      
      // Check if there are active filters
      if (Object.keys(searchState.activeFilters).length > 0) {
        // Add Clear All button
        const clearAllHtml = `
          <div class="flex items-center">
            <span class="font-medium text-gray-600 mr-2">Search:</span>
            <button id="clear-all-filters" class="bg-red-500 text-white hover:bg-red-600 text-xs ml-1 flex items-center px-2 py-1 rounded">
              <i class="ti ti-trash mr-1"></i>Clear All
            </button>
          </div>
        `;
        $(elements.activeFiltersContainer).append(clearAllHtml);
        
        // Create badges for each filter group
        Object.values(searchState.activeFilters).forEach((filter) => {
          if (filter.values.length > 0) {
            const badgeHtml = `
              <div class="filter-tag inline-flex items-center px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs ml-2">
                <span class="font-medium mr-1">${filter.title}:</span>
                <div class="flex flex-wrap items-center">
                  ${filter.values
                    .map(
                      (value, index) => `
                    <div class="flex items-center mr-1 last:mr-0">
                      <span>${value}</span>
                      <button class="remove-filter ml-1 text-blue-800 hover:text-blue-600"
                             data-field="${filter.field}"
                             data-value="${value}">
                        <i class="ti ti-circle-x"></i>
                      </button>
                      ${index < filter.values.length - 1 ? '<span class="mx-1">|</span>' : ''}
                    </div>
                  `
                    )
                    .join('')}
                </div>
              </div>
            `;
    
            $(elements.activeFiltersContainer).append(badgeHtml);
          }
        });
      }
    }
    
    /**
     * Apply active filters to the table
     */
    function applyFilters() {
      const searchState = AppUtils.AdvancedTableSearch.searchState;
      
      // Reset table first
      table.clearFilter();
      
      // If no filters, reset completely
      if (Object.keys(searchState.activeFilters).length === 0) {
        resetTable();
        return;
      }
      
      // Custom filter function
      function customFilter(data) {
        // Check if current row or its children match filters
        function checkRowAndChildren(rowData) {
          // Check if row matches all filter conditions
          const directMatch = Object.keys(searchState.activeFilters).every((field) => {
            const values = searchState.activeFilters[field].values;
            return values.some(
              (filterValue) => {
                const { operator, value } = AppUtils.AdvancedTableSearch.parseSearchTerm(filterValue);
                return AppUtils.AdvancedTableSearch.operators[operator](
                  rowData[field], 
                  value
                );
              }
            );
          });
          
          if (directMatch) return true;
          
          // Check nested children
          if (rowData._children && rowData._children.length) {
            return rowData._children.some((child) => checkRowAndChildren(child));
          }
          
          return false;
        }
        
        return checkRowAndChildren(data);
      }
      
      // Apply filter
      table.setFilter(customFilter);
      
      // Redraw and expand matching rows
      table.redraw(true);
      expandMatchingRows();
    }
    
    /**
     * Reset table to initial state
     */
    function resetTable() {
      const searchState = AppUtils.AdvancedTableSearch.searchState;
      
      // Clear search input
      $(elements.searchInput).val('');
      
      // Hide clear button
      $(elements.clearSearchBtn).addClass('hidden');
      
      // Reset search state
      searchState.activeFilters = {};
      
      // Clear active filters display
      $(elements.activeFiltersContainer).empty();
      
      // Clear table filter
      table.clearFilter();
      
      // Redraw table
      table.redraw(true);
      
      // Collapse all tree nodes
      table.getRows().forEach((row) => {
        if (row.getTreeChildren().length) {
          row.treeCollapse();
        }
      });
    }
    
    /**
     * Expand rows that match current filters
     */
    function expandMatchingRows() {
      const searchState = AppUtils.AdvancedTableSearch.searchState;
      
      // First collapse all rows
      table.getRows().forEach((row) => {
        if (row.getTreeChildren().length) {
          row.treeCollapse();
        }
      });
  
      // Expand rows with matching children
      if (Object.keys(searchState.activeFilters).length > 0) {
        table.getRows().forEach((row) => {
          const hasMatchingChild = row
            .getTreeChildren()
            .some((child) => AppUtils.AdvancedTableSearch.rowMatchesFilter(child, searchState.activeFilters));
  
          if (hasMatchingChild) {
            row.treeExpand();
            expandChildrenWithMatches(row);
          }
        });
      }
    }
    
    /**
     * Recursively expand children with matches
     * @param {Object} parentRow - Parent row component
     */
    function expandChildrenWithMatches(parentRow) {
      const searchState = AppUtils.AdvancedTableSearch.searchState;
      
      parentRow.getTreeChildren().forEach((childRow) => {
        const hasMatchingChild = childRow
          .getTreeChildren()
          .some((child) => AppUtils.AdvancedTableSearch.rowMatchesFilter(child, searchState.activeFilters));
  
        if (hasMatchingChild) {
          childRow.treeExpand();
          expandChildrenWithMatches(childRow);
        }
      });
    }
    
    /**
     * Set up event listeners for search functionality
     */
    function setupEventListeners() {
      // Debounced search input handling
      $(elements.searchInput).on(
        'input',
        AppUtils.AdvancedTableSearch.utils.debounce(function () {
          const value = $(this).val();
          AppUtils.AdvancedTableSearch.searchState.currentSearchTerm = value;
  
          if (value) {
            showSuggestions(value);
            $(elements.clearSearchBtn).removeClass('hidden');
            table.redraw(true);
          } else {
            $(elements.searchSuggestions).addClass('hidden');
            $(elements.clearSearchBtn).addClass('hidden');
            table.redraw(true);
          }
        }, AppUtils.AdvancedTableSearch.config.searchDebounceTime)
      );
  
      // Handle suggestion item clicks
      $(document).on('click', '.suggestion-item', function () {
        const field = $(this).data('field');
        const value = $(this).data('value');
        const title = $(this).data('title');
  
        AppUtils.AdvancedTableSearch.addFilter(field, value, title);
        updateFilterBadges();
        applyFilters();
        
        $(elements.searchInput).val('').focus();
        $(elements.searchSuggestions).addClass('hidden');
      });
  
      // Handle filter removal
      $(document).on('click', '.remove-filter', function () {
        const field = $(this).data('field');
        const value = $(this).data('value');
  
        AppUtils.AdvancedTableSearch.removeFilter(field, value);
        updateFilterBadges();
        applyFilters();
        
        table.redraw(true);
      });
  
      // Clear all filters
      $(document).on('click', '#clear-all-filters', function() {
        resetTable();
      });
  
      // Hide suggestions when clicking outside
      $(document).on('click', function (e) {
        if (!$(e.target).closest('#advanced-search-suggestions, #advanced-search-input').length) {
          $(elements.searchSuggestions).addClass('hidden');
        }
      });
    }
    
    // Initialize event listeners
    setupEventListeners();
    
    // Return table instance with utility methods
    return {
      table,
      resetTable,
      applyFilters,
      updateFilterBadges
    };
  }
};

// Ensure global accessibility
window.AppUtils = AppUtils;