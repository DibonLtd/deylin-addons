/** @odoo-module **/

/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { _t } from "@web/core/l10n/translation";
import { renderToElement } from "@web/core/utils/render";
import { jsonrpc } from "@web/core/network/rpc_service";

publicWidget.registry.SurveyUploadFile = publicWidget.Widget.extend({
    selector: '.upload-files',

    init: function (parent, options) {
        this._super.apply(this, arguments);
        this.file_loaded = false;
        this.readonly = options.readonly;
        this.options = options.readonly;
    },

    start: function () {
        var self = this;
        var $inputFile = this.$target.find(".input-file");
        var files_ids = [];
        var res_model = $inputFile.attr('res-model');
        var res_id = $inputFile.attr('data-res-id');
        var multifile = $inputFile.attr('multi-file');
        var ufiles = this.$target.find('input');

        var show_del = $inputFile.attr('show-delete') === "true";
        var show_download = $inputFile.attr('show-download') === "true";
        multifile = multifile === "true";

        if (this.readonly !== undefined) {
            show_del = !this.readonly;
            show_download = !this.readonly;
        }

        var totalfilesize = 0;
        var MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB

        $inputFile.uploadFile({
            url: '/upload/attachment/onchange',
            fileName: 'attachments',
            multiple: multifile,
            maxFileCount: multifile ? 99 : 15,
            maxFileSize: MAX_FILE_SIZE,
            showDelete: show_del,
            showDownload: show_download,
            formData: { 'res_id': res_id, 'res_model': res_model },

            onSelect: function (files) {
                let totalfilesize_select = 0;
                for (let i = 0; i < files.length; i++) {
                    totalfilesize_select += files[i].size;
                }
                if ((totalfilesize + totalfilesize_select) > MAX_FILE_SIZE) {
                    alert("The maximum size for all your attachments is 10 MB. Please compress or split your files.");
                    return false;
                }
                totalfilesize += totalfilesize_select;
                return true;
            },

            deleteCallback: function (data, pd) {
                jsonrpc('/upload/attachment/delete', {
                    'attachment_id': data,
                }).then(function (response) {
                    var index = files_ids.indexOf(response[0]);
                    if (index > -1) {
                        files_ids.splice(index, 1);
                        totalfilesize -= response[1];
                    }
                    ufiles.val(files_ids.toString());
                });
            },

            onLoad: function (obj) {
                jsonrpc('/upload/attachment/onload', {
                    'res_model': res_model,
                    'res_id': res_id,
                    'files_ids': ufiles.val()
                }).then(function (data) {
                    for (var i = 0; i < data.length; i++) {
                        obj.createProgress(data[i]["path"], data[i]["name"], data[i]["size"]);
                        files_ids.push(data[i]["path"]);
                        totalfilesize += data[i]["size"];
                    }
                    ufiles.val(files_ids.toString());
                    if (data.length <= 0) {
                        var $noattachment = $('form').find('.no-attachment');
                        if ($noattachment.length <= 0) {
                            $noattachment = $('div').find('.no-attachment');
                        }
                        if ($noattachment.length > 0) {
                            $noattachment.show();
                        }
                    }
                    self.file_loaded = true;
                })
            },

            onSuccess: function (files, response, xhr, pd) {
                files_ids.push(response);
                ufiles.val(files_ids.toString());
            },

            downloadCallback: function (filename, pd) {
                window.open("/web/content/" + filename, '_blank');
            },

            uploadButtonClass: "btn browse-btn",
            uploadStr: '<i class="fa fa-paperclip"></i>  &#160; Select Files',
            dragDropStr: "<span><b>Drag &amp; Drop Files Here</b></span>",
            sizeErrorStr: "is not allowed. Maximum file size is 10 MB.",
            maxFileCountErrorStr: " is not allowed. Maximum allowed files are: ",
            statusBarWidth: 350,
            dragdropWidth: 350,
        });

        if (show_del === false) {
            $inputFile.hide('form');
        }

        $('.btn-bs-file input').on('change', function (event) {
            var file_text = $(this).parent().parent().find('span');
            if (this.files.length > 1) {
                file_text.text(this.files.length + ' files selected');
            } else if (this.files.length == 1) {
                file_text.text(this.files[0].name);
            } else {
                file_text.text('No file chosen');
            }
        });
    },
});
