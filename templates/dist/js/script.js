function toggleCategoriesChechbox() {
  const categoriesLabels = document.querySelectorAll('.catefories__list--label');
  if (!categoriesLabels) return;

  categoriesLabels.forEach((label) => {
    label.addEventListener('click', () => {
      const checkboxInput = label.querySelector('.catefories__list--checkbox input');
      checkboxInput.checked ? label.classList.add('checked') : label.classList.remove('checked');
    });
  });
}

function selectSubscriptionOption() {
  const subscriptionContainer = document.querySelector('.subscribtion__select');
  if (!subscriptionContainer) return;

  subscriptionContainer.addEventListener('click', (event) => {
    const clickedOption = event.target.closest('.subscribtion__select--option');

    if (clickedOption && !clickedOption.classList.contains('active')) {
      const subscriptionOptions = subscriptionContainer.querySelectorAll(
        '.subscribtion__select--option'
      );

      subscriptionOptions.forEach((option) => {
        option.classList.remove('active');
      });

      clickedOption.classList.add('active');
    }
  });
}

toggleCategoriesChechbox();
selectSubscriptionOption();
