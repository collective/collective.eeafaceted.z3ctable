// (un)select every checkboxes
function toggleCheckboxes(checkBoxId) {
    checkbox = $('input#select_unselect_items');
    if (checkbox[0].checked) {
        $('input[name="' + checkBoxId + '"]').each(function() {
            this.checked = true;
        });
    }
    else {
        $('input[name="' + checkBoxId + '"]').each(function() {
            this.checked = false;
        });
    }
}

// helper method that returns selected checkboxes
function selectedCheckBoxes(checkBoxId) {
    selected_boxes = [];
    i = 0;
    $('input[name="' + checkBoxId + '"]').each(function() {
        if (this.checked) {
            selected_boxes[i] = this.value;
            i = i + 1;
        }
    });
    return selected_boxes;
}
