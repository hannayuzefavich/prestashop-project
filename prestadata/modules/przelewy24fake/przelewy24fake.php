<?php
if (!defined('_PS_VERSION_')) {
    exit;
}

class Przelewy24Fake extends PaymentModule
{
    public function __construct()
    {
        $this->name = 'przelewy24fake';
        $this->tab = 'payments_gateways';
        $this->version = '1.0.0';
        $this->author = 'Custom';
        $this->controllers = ['payment', 'validation'];
        $this->is_eu_compatible = 1;

        parent::__construct();

        $this->displayName = $this->l('Przelewy24');
        $this->description = $this->l('Przelewy24');
    }

    public function install()
    {
        return parent::install() &&
            $this->registerHook('paymentOptions');
    }

    public function hookPaymentOptions($params)
	{
		$payment_options = [];

		$newOption = new PrestaShop\PrestaShop\Core\Payment\PaymentOption();
		$newOption->setCallToActionText($this->l('Przelewy24'))
			->setAction($this->context->link->getModuleLink($this->name, 'payment', [], true))
			->setAdditionalInformation(
				'<style>@import url("'.__PS_BASE_URI__.'modules/'.$this->name.'/views/css/style.css");</style>'.
				'<img src="'.Media::getMediaPath(_PS_MODULE_DIR_.$this->name.'/views/img/logo.png').'" class="payment-logo" alt="Przelewy24">'
			);

		$payment_options[] = $newOption;

		return $payment_options;
	}

}
