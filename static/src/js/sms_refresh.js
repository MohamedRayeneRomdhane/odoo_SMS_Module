odoo.define('sms_tunisiesms.refresh_views', function (require) {
    "use strict";
    
    var core = require('web.core');
    var session = require('web.session');
    var rpc = require('web.rpc');
    var web_client = require('web.web_client');
    
    // Auto-refresh SMS views every 30 seconds
    var SMS_REFRESH_INTERVAL = 30000; // 30 seconds
    
    function refreshSMSViews() {
        // Check if user has SMS access and refresh if needed
        rpc.query({
            route: '/sms/check_access',
            params: {}
        }).then(function(result) {
            if (!result.has_access) {
                // User doesn't have access, trigger refresh
                rpc.query({
                    route: '/sms/refresh_access',
                    params: {}
                }).then(function(refresh_result) {
                    if (refresh_result.success) {
                        // Force page reload to get fresh permissions
                        window.location.reload();
                    }
                });
            }
        }).catch(function(error) {
            console.log('SMS access check failed:', error);
        });
    }
    
    function forceViewRefresh() {
        // Force refresh of current view if it's SMS-related
        if (web_client.action_manager && web_client.action_manager.inner_widget) {
            var current_widget = web_client.action_manager.inner_widget;
            if (current_widget && current_widget.modelName) {
                var modelName = current_widget.modelName;
                if (modelName === 'sms.tunisiesms.history' || 
                    modelName === 'sms.tunisiesms.queue' ||
                    modelName === 'sms.tunisiesms') {
                    
                    // Trigger view refresh
                    if (current_widget.reload) {
                        current_widget.reload();
                    } else if (current_widget.do_action) {
                        current_widget.do_action({
                            type: 'ir.actions.act_window',
                            res_model: modelName,
                            view_mode: 'list,form',
                            target: 'current',
                        });
                    }
                }
            }
        }
    }
    
    // Start auto-refresh when page loads
    $(document).ready(function() {
        // Set up periodic refresh
        setInterval(function() {
            refreshSMSViews();
            forceViewRefresh();
        }, SMS_REFRESH_INTERVAL);
        
        // Also refresh on focus (when user switches back to tab)
        $(window).focus(function() {
            refreshSMSViews();
            forceViewRefresh();
        });
    });
    
    return {
        refreshSMSViews: refreshSMSViews,
        forceViewRefresh: forceViewRefresh
    };
});
