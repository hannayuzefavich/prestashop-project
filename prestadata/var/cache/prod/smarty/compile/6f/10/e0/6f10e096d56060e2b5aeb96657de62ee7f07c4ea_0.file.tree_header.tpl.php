<?php
/* Smarty version 3.1.48, created on 2024-11-17 19:53:12
  from '/var/www/html/admin226btygwb/themes/default/template/helpers/tree/tree_header.tpl' */

/* @var Smarty_Internal_Template $_smarty_tpl */
if ($_smarty_tpl->_decodeProperties($_smarty_tpl, array (
  'version' => '3.1.48',
  'unifunc' => 'content_673a3b980c4809_30250919',
  'has_nocache_code' => false,
  'file_dependency' => 
  array (
    '6f10e096d56060e2b5aeb96657de62ee7f07c4ea' => 
    array (
      0 => '/var/www/html/admin226btygwb/themes/default/template/helpers/tree/tree_header.tpl',
      1 => 1731867046,
      2 => 'file',
    ),
  ),
  'includes' => 
  array (
  ),
),false)) {
function content_673a3b980c4809_30250919 (Smarty_Internal_Template $_smarty_tpl) {
?><div class="tree-panel-heading-controls clearfix">
	<?php if ((isset($_smarty_tpl->tpl_vars['title']->value))) {?><i class="icon-tag"></i>&nbsp;<?php echo call_user_func_array( $_smarty_tpl->smarty->registered_plugins[Smarty::PLUGIN_FUNCTION]['l'][0], array( array('s'=>$_smarty_tpl->tpl_vars['title']->value),$_smarty_tpl ) );
}?>
	<?php if ((isset($_smarty_tpl->tpl_vars['toolbar']->value))) {
echo $_smarty_tpl->tpl_vars['toolbar']->value;
}?>
</div>
<?php }
}
