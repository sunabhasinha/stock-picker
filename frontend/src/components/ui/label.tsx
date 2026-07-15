// shadcn/ui label (plain-element variant) - vendored source (ADR-0007).
import * as React from "react";
import { cn } from "@/lib/utils";

export const Label = React.forwardRef<HTMLLabelElement, React.LabelHTMLAttributes<HTMLLabelElement>>(
  ({ className, ...props }, ref) => (
    <label
      ref={ref}
      className={cn("text-xs font-medium text-muted-foreground", className)}
      {...props}
    />
  )
);
Label.displayName = "Label";
