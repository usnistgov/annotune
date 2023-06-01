const select = document.querySelector(".suggestion");
const label = document.querySelector(".text_input");
const submitButton = document.querySelector("#myBtn");
console.log({ select, submitButton });

submitButton.disabled = true;

let selectValue;
let labelValue;

select.addEventListener("change", (e) => {
  selectValue = e.target.value;
  checkButtonEnabled();
});

label.addEventListener("change", (e) => {
  labelValue = e.target.value;
  checkButtonEnabled();
});

function checkButtonEnabled() {
  if (selectValue && labelValue) {
    submitButton.disabled = true;
  } else if (selectValue || labelValue) {
    submitButton.disabled = false;
  }
}
