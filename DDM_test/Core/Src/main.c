#include "stm32f1xx_hal.h"

int main(void)
{
    HAL_Init();

    __HAL_RCC_GPIOA_CLK_ENABLE();
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Pin = GPIO_PIN_0;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

    // Main loop
    while (1)
    {
      HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_0); // Toggle the LED
      HAL_Delay(500); // Delay for 500 milliseconds
        // Your application code here
    }
}