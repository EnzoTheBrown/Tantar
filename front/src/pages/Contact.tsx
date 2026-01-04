
import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { Link } from "react-router-dom";
import { Checkbox } from "@/components/ui/checkbox";
import { 
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage 
} from "@/components/ui/form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { PublicLayout } from "@/components/PublicLayout";

// Form validation schema
const formSchema = z.object({
  firstName: z.string().min(2, { message: "Le prénom doit contenir au moins 2 caractères" }),
  lastName: z.string().min(2, { message: "Le nom doit contenir au moins 2 caractères" }),
  company: z.string().min(2, { message: "L'entreprise doit être spécifiée" }),
  position: z.string().min(2, { message: "La fonction doit être spécifiée" }),
  email: z.string().email({ message: "Veuillez entrer une adresse email valide" }),
  phone: z.string().optional(),
  message: z.string().min(10, { message: "Votre message doit contenir au moins 10 caractères" }),
  acceptTerms: z.boolean().refine(val => val === true, {
    message: "Vous devez accepter les conditions d'utilisation"
  })
});

const Contact = () => {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      firstName: "",
      lastName: "",
      company: "",
      position: "",
      email: "",
      phone: "",
      message: "",
      acceptTerms: false
    },
  });

  const onSubmit = (values: z.infer<typeof formSchema>) => {
    setIsSubmitting(true);
    
    // Simulate form submission
    setTimeout(() => {
      toast.success("Votre message a bien été envoyé. Nous vous contacterons bientôt.");
      form.reset();
      setIsSubmitting(false);
    }, 1000);
  };

  return (
    <PublicLayout>
      <div className="container mx-auto px-6">
        <h1 className="text-4xl font-bold mb-4 text-center">Contactez-nous</h1>
        <p className="text-lg text-center mb-12 max-w-3xl mx-auto">
          Notre équipe est à votre disposition pour répondre à toutes vos questions concernant Tantar.
        </p>
        
        <div className="max-w-3xl mx-auto">
          {/* Contact Form */}
          <div className="bg-white/10 backdrop-blur-sm rounded-lg border border-blue-800 p-8 shadow-xl">
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <FormField
                    control={form.control}
                    name="firstName"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-white">Prénom</FormLabel>
                        <FormControl>
                          <Input 
                            {...field} 
                            className="bg-white/20 border-blue-800 text-white placeholder:text-white/60"
                            placeholder="Votre prénom" 
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="lastName"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-white">Nom</FormLabel>
                        <FormControl>
                          <Input 
                            {...field} 
                            className="bg-white/20 border-blue-800 text-white placeholder:text-white/60"
                            placeholder="Votre nom" 
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="company"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-white">Entreprise</FormLabel>
                        <FormControl>
                          <Input 
                            {...field} 
                            className="bg-white/20 border-blue-800 text-white placeholder:text-white/60"
                            placeholder="Nom de votre entreprise" 
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="position"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-white">Fonction</FormLabel>
                        <FormControl>
                          <Input 
                            {...field} 
                            className="bg-white/20 border-blue-800 text-white placeholder:text-white/60"
                            placeholder="Votre fonction" 
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="email"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-white">Email</FormLabel>
                        <FormControl>
                          <Input 
                            {...field} 
                            type="email"
                            className="bg-white/20 border-blue-800 text-white placeholder:text-white/60"
                            placeholder="votre@email.com" 
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="phone"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-white">Téléphone (optionnel)</FormLabel>
                        <FormControl>
                          <Input 
                            {...field} 
                            className="bg-white/20 border-blue-800 text-white placeholder:text-white/60"
                            placeholder="Votre numéro de téléphone" 
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
                
                <FormField
                  control={form.control}
                  name="message"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-white">Votre message</FormLabel>
                      <FormControl>
                        <Textarea 
                          {...field} 
                          className="min-h-[120px] bg-white/20 border-blue-800 text-white placeholder:text-white/60"
                          placeholder="Décrivez votre besoin ou votre question..." 
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="acceptTerms"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                      <FormControl>
                        <Checkbox
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                      <div className="space-y-1 leading-none">
                        <FormLabel className="text-sm text-white/80">
                          J'accepte que mes informations personnelles soient utilisées par Tantar dans le cadre du traitement de ma demande.
                        </FormLabel>
                        <FormMessage />
                      </div>
                    </FormItem>
                  )}
                />
                
                <Button 
                  type="submit" 
                  className="w-full bg-blue-600 hover:bg-blue-700" 
                  disabled={isSubmitting}
                >
                  {isSubmitting ? "Envoi en cours..." : "Envoyer ma demande"}
                </Button>
              </form>
            </Form>
          </div>
        </div>
      </div>
    </PublicLayout>
  );
};

export default Contact;
