const listChecks = document.getElementsByClassName("check");
const mainCheck = document.getElementById("master-check")

function switchCheck()  {
  for (const eachElement of listChecks) {
    eachElement.checked = mainCheck.checked;
  }
}

mainCheck.onclick = switchCheck;
