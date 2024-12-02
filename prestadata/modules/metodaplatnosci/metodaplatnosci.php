<?php
if (!defined('_PS_VERSION_')) {
    exit;
}

class MetodaPlatnosci extends Module
{
    public function __construct()
    {
        $this->name = 'metodaplatnosci';
        $this->tab = 'front_office_features';
        $this->version = '1.0.0';
        $this->author = 'Custom';
        $this->need_instance = 0;

        parent::__construct();

        $this->displayName = $this->l('Metody płatności');
        $this->description = $this->l('Displays custom payment methods and reviews in the footer.');
        $this->ps_versions_compliancy = ['min' => '1.7.0.0', 'max' => _PS_VERSION_];
    }

    public function install()
    {
        return parent::install() && $this->registerHook('displayFooter');
    }

    public function uninstall()
    {
        return parent::uninstall();
    }

    public function hookDisplayFooter($params)
    {
        return $this->display(__FILE__, 'views/templates/hook/displayfooter.tpl');
    }
}
