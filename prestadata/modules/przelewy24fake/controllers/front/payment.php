<?php
class Przelewy24FakePaymentModuleFrontController extends ModuleFrontController
{
    public function postProcess()
    {
        // Завершение заказа
        $cart = $this->context->cart;
        if (!$this->module->active || !$cart) {
            Tools::redirect('index.php?controller=order&step=1');
        }

        // Установка статуса заказа (например, "Ожидание оплаты")
        $orderStatusId = Configuration::get('PS_OS_PREPARATION');
        $this->module->validateOrder(
            (int)$cart->id,
            $orderStatusId,
            (float)$cart->getOrderTotal(true),
            $this->module->displayName,
            null,
            [],
            (int)$cart->id_currency,
            false,
            $this->context->customer->secure_key
        );

        // Редирект на страницу подтверждения заказа
        $order = new Order((int)$this->module->currentOrder);
        Tools::redirect('index.php?controller=order-confirmation&id_cart='.(int)$cart->id.
            '&id_module='.(int)$this->module->id.
            '&id_order='.(int)$this->module->currentOrder.
            '&key='.$this->context->customer->secure_key);
    }
}
