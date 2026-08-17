document.addEventListener('DOMContentLoaded', () => {

const dropdowns = document.querySelectorAll('[data-category-dropdown]');

    dropdowns.forEach((dropdown) => {

        const toggle =dropdown.querySelector('[data-category-toggle]');

        const input = dropdown.querySelector('[data-category-input]');

        const label = dropdown.querySelector('[data-category-label]');

        const options = dropdown.querySelectorAll('[data-category-option]');

        if (!toggle || !input || !label) { return; }

        const dropdownInstance = bootstrap.Dropdown.getOrCreateInstance(toggle);

        let hideTimer = null;

        const updateSelectedCategory = () => {
            let selectedOption = null;

            options.forEach((option) => {
                const isSelected = option.dataset.categoryValue === input.value;
                option.classList.toggle('active', isSelected);

                if (isSelected) {
                    selectedOption = option;
                }
            });

            if (selectedOption) {
                label.textContent =
                    selectedOption.textContent.trim();
            }
        };

        updateSelectedCategory();

        options.forEach((option) => {
            option.addEventListener('click', () => {
                input.value = option.dataset.categoryValue;
                updateSelectedCategory();
                dropdownInstance.hide();
                toggle.focus();
            });
        });

        dropdown.addEventListener('mouseleave', () => {
            hideTimer = setTimeout(() => {
                dropdownInstance.hide();
            }, 150);
        });

        dropdown.addEventListener('mouseenter', () => {

            if (hideTimer !== null) {
                clearTimeout(hideTimer);
                hideTimer = null;
            }
        });
    });

const statusDropdowns = document.querySelectorAll('[data-status-dropdown]');

statusDropdowns.forEach((dropdown) => {

    const toggle = dropdown.querySelector('[data-status-toggle]');

    const input = dropdown.querySelector('[data-status-input]');

    const label = dropdown.querySelector('[data-status-label]');

    const options = dropdown.querySelectorAll('[data-status-option]');

    if (!toggle || !input || !label) { return; }

    const dropdownInstance = bootstrap.Dropdown.getOrCreateInstance(toggle);

    let hideTimer = null;

    const updateSelectedStatus = () => {
        let selectedOption = null;

        options.forEach((option) => {
            const isSelected =
                option.dataset.statusValue === input.value;

            option.classList.toggle('active', isSelected);

            if (isSelected) {
                selectedOption = option;
            }
        });

        if (selectedOption) {
            label.textContent =
                selectedOption.textContent.trim();
        }
    };
    updateSelectedStatus();

    options.forEach((option) => {
        option.addEventListener('click', () => {

            input.value = option.dataset.statusValue;

            updateSelectedStatus();

            dropdownInstance.hide();

            toggle.focus();
        });
    });

    dropdown.addEventListener('mouseleave', () => {
        hideTimer = setTimeout(() => {
            dropdownInstance.hide();
        }, 150);
    });

    dropdown.addEventListener('mouseenter', () => {

        if (hideTimer !== null) {
            clearTimeout(hideTimer);
            hideTimer = null;
        }
    });
});
});