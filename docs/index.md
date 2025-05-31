# Introduction

FletGemini for Flet.

## Examples

```
import flet as ft

from flet_gemini import FletGemini


def main(page: ft.Page):
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    page.add(

                ft.Container(height=150, width=300, alignment = ft.alignment.center, bgcolor=ft.Colors.PURPLE_200, content=FletGemini(
                    tooltip="My new FletGemini Control tooltip",
                    value = "My new FletGemini Flet Control", 
                ),),

    )


ft.app(main)
```

## Classes

[FletGemini](FletGemini.md)


