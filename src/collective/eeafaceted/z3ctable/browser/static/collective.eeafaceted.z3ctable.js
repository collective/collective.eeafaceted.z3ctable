// (un)select every checkboxes
function toggleCheckboxes(checkbox, checkBoxId) {
    if (checkbox.checked) {
        $('input[name="' + checkBoxId + '"]').each(function() {
            if (this.checked == false) {
                this.checked = true;
                this.dispatchEvent(new Event('click'));
            }
        });
    }
    else {
        $('input[name="' + checkBoxId + '"]').each(function() {
            if (this.checked == true) {
                this.checked = false;
                this.dispatchEvent(new Event('click'));
            }
        });
    }
}

// helper method that returns selected checkboxes
function selectedCheckBoxes(checkBoxId) {
    selected_boxes = [];
    i = 0;
    $('input[name="' + checkBoxId + '"]:not(#select_unselect_items)').each(function() {
        if (this.checked) {
            selected_boxes[i] = this.value;
            i = i + 1;
        }
    });
    return selected_boxes;
}
